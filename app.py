import os, glob, shutil, zipfile, tempfile, json
from pathlib import Path
import gradio as gr
import numpy as np
from PIL import Image, ImageOps
from deepface import DeepFace

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data" if Path("/data").exists() else "./data"))
GALLERY_DIR = DATA_DIR / "gallery"
GALLERY_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = DATA_DIR / "config.json"
MODEL_NAME = "Facenet512"
DISTANCE_THRESHOLD = 0.40

def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"event_name": "Event Photo Finder", "message": "Upload a selfie to find your event photos."}

def save_config(event_name, message):
    cfg={"event_name": (event_name or "Event Photo Finder").strip(),
         "message": (message or "").strip()}
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"Saved event settings for: {cfg['event_name']}"

def file_path(file):
    if file is None: return None
    if isinstance(file, str): return file
    if isinstance(file, dict): return file.get("path") or file.get("name")
    return getattr(file, "name", None)

def add_gallery_files(files):
    if not files: return "Select one or more images first."
    count=0
    for f in files:
        src=file_path(f)
        if not src or not os.path.isfile(src): continue
        ext=Path(src).suffix.lower()
        if ext not in {".jpg",".jpeg",".png",".webp",".bmp"}: continue
        dest=GALLERY_DIR / (Path(src).name)
        # Avoid overwrite collisions
        if dest.exists():
            dest=GALLERY_DIR / f"{Path(src).stem}_{count}{ext}"
        shutil.copy2(src, dest)
        count+=1
    return f"Added {count} image(s). Gallery now contains {len(gallery_files())} images."

def gallery_files():
    files=[]
    for ext in ("*.jpg","*.jpeg","*.png","*.webp","*.bmp"):
        files.extend(glob.glob(str(GALLERY_DIR/ext)))
    return sorted(files)

def clear_gallery():
    for f in gallery_files():
        try: os.remove(f)
        except: pass
    return "Gallery cleared.", []

def gallery_preview():
    return [(f, Path(f).name) for f in gallery_files()]

def get_embedding(img_path):
    reps=DeepFace.represent(img_path=img_path, model_name=MODEL_NAME,
                            detector_backend="opencv", enforce_detection=True,
                            align=True, normalization="base")
    if not reps: return None
    return np.asarray(reps[0]["embedding"], dtype=np.float32)

def cosine_distance(a,b):
    denom=np.linalg.norm(a)*np.linalg.norm(b)
    if denom==0: return 1.0
    return float(1.0-np.dot(a,b)/denom)

def match_faces(selfie):
    cfg=load_config()
    if selfie is None:
        return "Please upload or capture a selfie.", []
    gallery=gallery_files()
    if not gallery:
        return "The event gallery is empty. Ask the organizer to add photos.", []
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        selfie_path=tmp.name
    try:
        im=Image.fromarray(selfie.astype("uint8")) if isinstance(selfie,np.ndarray) else Image.open(selfie)
        im=ImageOps.exif_transpose(im).convert("RGB")
        im.save(selfie_path, quality=95)
        emb=get_embedding(selfie_path)
        if emb is None: return "No face detected in your selfie. Try another photo.", []
        results=[]
        for p in gallery:
            try:
                cand=get_embedding(p)
                if cand is None: continue
                dist=cosine_distance(emb,cand)
                if dist <= DISTANCE_THRESHOLD:
                    results.append((dist,p))
            except Exception:
                continue
        results.sort(key=lambda x:x[0])
        matches=[p for _,p in results]
        if not matches:
            return "No close matches found. Try a clear, front-facing selfie.", []
        return f"Found {len(matches)} matching photo(s) for {cfg.get('event_name','your event')}!", [(p,Path(p).name) for p in matches]
    except Exception as e:
        return f"Face matching failed: {type(e).__name__}: {e}", []
    finally:
        try: os.remove(selfie_path)
        except: pass

def make_zip(gallery):
    if not gallery: return None
    selected=[]
    for item in gallery:
        if isinstance(item, (tuple,list)): item=item[0]
        if isinstance(item,str) and os.path.isfile(item): selected.append(item)
    if not selected: return None
    tmp=tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.close()
    with zipfile.ZipFile(tmp.name,"w",zipfile.ZIP_DEFLATED) as z:
        for i,p in enumerate(selected):
            z.write(p, arcname=f"{i+1}_{Path(p).name}")
    return tmp.name

cfg=load_config()
with gr.Blocks(theme=gr.themes.Soft(), title=cfg.get("event_name","Event Photo Finder")) as demo:
    gr.Markdown("# 📸 Event Photo Finder")
    gr.Markdown(cfg.get("message","Upload a selfie to find your event photos."))
    with gr.Tab("Find My Photos"):
        selfie=gr.Image(label="Upload or take a selfie", sources=["upload","webcam"], type="numpy")
        find_btn=gr.Button("🔍 Find My Photos", variant="primary")
        status=gr.Markdown()
        matches=gr.Gallery(label="Matching Photos", columns=3, height="auto", object_fit="contain")
        zip_btn=gr.Button("📦 Prepare ZIP of Matches")
        zip_out=gr.File(label="Download matching photos (ZIP)")
        find_btn.click(match_faces, inputs=selfie, outputs=[status,matches])
        zip_btn.click(make_zip, inputs=matches, outputs=zip_out)
    with gr.Tab("Organizer"):
        gr.Markdown("### Event settings")
        event_name=gr.Textbox(label="Event name", value=cfg.get("event_name","Event Photo Finder"))
        event_message=gr.Textbox(label="Message shown to guests", value=cfg.get("message","Upload a selfie to find your event photos."), lines=2)
        save_btn=gr.Button("Save event settings")
        save_status=gr.Textbox(label="Status", interactive=False)
        save_btn.click(save_config, inputs=[event_name,event_message], outputs=save_status)
        gr.Markdown("### Add gallery photos")
        gallery_upload=gr.File(label="Choose event photos", file_count="multiple", file_types=["image"])
        add_btn=gr.Button("Add Photos to Gallery")
        add_status=gr.Textbox(label="Upload status", interactive=False)
        add_btn.click(add_gallery_files, inputs=gallery_upload, outputs=add_status)
        refresh_btn=gr.Button("Refresh gallery preview")
        preview=gr.Gallery(label="Current event gallery", columns=4, height="auto")
        refresh_btn.click(gallery_preview, inputs=None, outputs=preview)
        clear_btn=gr.Button("Clear Gallery", variant="stop")
        clear_status=gr.Textbox(label="Clear status", interactive=False)
        clear_btn.click(clear_gallery, inputs=None, outputs=[clear_status,preview])
        demo.load(gallery_preview, inputs=None, outputs=preview)

if __name__ == "__main__":
    demo.launch()
