import os, json, shutil, tempfile, zipfile
from pathlib import Path
import gradio as gr
import spaces
import torch
import numpy as np
from PIL import Image, ImageOps
from facenet_pytorch import MTCNN, InceptionResnetV1

DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
GALLERY_DIR = DATA_DIR / "gallery"
GALLERY_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = DATA_DIR / "config.json"
MATCH_THRESHOLD = 0.70  # cosine similarity; tune with real event images

def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"event_name": "Event Photo Finder", "message": "Upload or take a selfie to find your event photos."}

def save_config(event_name, message):
    cfg = {"event_name": (event_name or "Event Photo Finder").strip(),
           "message": (message or "").strip()}
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"Saved settings for {cfg['event_name']}."

def file_path(f):
    if f is None: return None
    if isinstance(f, str): return f
    if isinstance(f, dict): return f.get("path") or f.get("name")
    return getattr(f, "name", None)

def gallery_files():
    out=[]
    for ext in ("*.jpg","*.jpeg","*.png","*.webp","*.bmp"):
        out.extend(GALLERY_DIR.glob(ext))
    return sorted(str(p) for p in out)

def add_gallery_files(files):
    if not files: return "Select photos first."
    count=0
    for f in files:
        src=file_path(f)
        if not src or not os.path.isfile(src): continue
        ext=Path(src).suffix.lower()
        if ext not in {".jpg",".jpeg",".png",".webp",".bmp"}: continue
        dest=GALLERY_DIR/Path(src).name
        if dest.exists():
            dest=GALLERY_DIR/f"{Path(src).stem}_{count}{ext}"
        shutil.copy2(src,dest)
        count+=1
    return f"Added {count} photo(s). Gallery contains {len(gallery_files())} photos."

def preview_gallery():
    return [(p,Path(p).name) for p in gallery_files()]

def clear_gallery():
    for p in gallery_files():
        try: os.remove(p)
        except OSError: pass
    return "Gallery cleared.", []

# Models are instantiated inside the GPU-decorated inference function.
@spaces.GPU
def find_matches_gpu(selfie_path, gallery_paths):
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    detector=MTCNN(image_size=160, margin=20, min_face_size=40,
                   thresholds=[0.6,0.7,0.7], factor=0.709,
                   post_process=True, device=device)
    model=InceptionResnetV1(pretrained="vggface2").eval().to(device)

    def embed(path):
        img=ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        face=detector(img)
        if face is None:
            return None
        if face.ndim==3:
            face=face.unsqueeze(0)
        with torch.no_grad():
            v=model(face.to(device)).detach().cpu().numpy()[0]
        norm=np.linalg.norm(v)
        if norm==0: return None
        return v/norm

    target=embed(selfie_path)
    if target is None:
        return [], "No face was detected in the selfie. Try a clear, front-facing image."

    found=[]
    for path in gallery_paths:
        try:
            v=embed(path)
            if v is None: continue
            similarity=float(np.dot(target,v))
            if similarity >= MATCH_THRESHOLD:
                found.append((similarity,path))
        except Exception:
            # Skip unsupported/corrupt photos or photos where inference fails.
            continue
    found.sort(key=lambda x:x[0],reverse=True)
    return [p for _,p in found], f"Found {len(found)} matching photo(s). Similarity threshold: {MATCH_THRESHOLD:.2f}"

def run_search(selfie):
    if selfie is None:
        return "Please upload or capture a selfie.", [], None
    files=gallery_files()
    if not files:
        return "The event gallery is empty. Organizer needs to add photos first.", [], None
    tmp_path=None
    try:
        if isinstance(selfie,np.ndarray):
            image=Image.fromarray(selfie.astype("uint8")).convert("RGB")
        else:
            image=Image.open(selfie).convert("RGB")
        image=ImageOps.exif_transpose(image)
        tmp=tempfile.NamedTemporaryFile(suffix=".jpg",delete=False)
        tmp_path=tmp.name
        tmp.close()
        image.save(tmp_path,quality=95)
        matches,msg=find_matches_gpu(tmp_path,files)
        gallery=[(p,Path(p).name) for p in matches]
        return msg,gallery,None
    except Exception as e:
        return f"Matching error: {type(e).__name__}: {e}", [], None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except OSError: pass

def create_zip(items):
    if not items: return None
    paths=[]
    for item in items:
        if isinstance(item,(list,tuple)): item=item[0]
        if isinstance(item,str) and os.path.isfile(item): paths.append(item)
    if not paths: return None
    tmp=tempfile.NamedTemporaryFile(suffix=".zip",delete=False)
    tmp.close()
    with zipfile.ZipFile(tmp.name,"w",zipfile.ZIP_DEFLATED) as z:
        for i,p in enumerate(paths):
            z.write(p,arcname=f"{i+1}_{Path(p).name}")
    return tmp.name

cfg=load_config()
with gr.Blocks(theme=gr.themes.Soft(), title=cfg.get("event_name","Event Photo Finder")) as demo:
    gr.Markdown("# 📸 Event Photo Finder")
    gr.Markdown(cfg.get("message","Upload or take a selfie to find your event photos."))
    with gr.Tab("Find My Photos"):
        selfie=gr.Image(label="Upload or take a selfie", sources=["upload","webcam"], type="numpy")
        search_btn=gr.Button("🔍 Find My Photos",variant="primary")
        status=gr.Markdown()
        results=gr.Gallery(label="Matching Photos",columns=3,height="auto",object_fit="contain")
        zip_btn=gr.Button("📦 Create ZIP of matches")
        zip_file=gr.File(label="Download ZIP")
        search_btn.click(run_search,inputs=selfie,outputs=[status,results,zip_file])
        zip_btn.click(create_zip,inputs=results,outputs=zip_file)
    with gr.Tab("Organizer"):
        gr.Markdown("### Event configuration")
        event_name=gr.Textbox(label="Event name",value=cfg.get("event_name","Event Photo Finder"))
        event_message=gr.Textbox(label="Guest message",value=cfg.get("message","Upload or take a selfie to find your event photos."),lines=2)
        save_btn=gr.Button("Save settings")
        save_status=gr.Textbox(label="Status",interactive=False)
        save_btn.click(save_config,inputs=[event_name,event_message],outputs=save_status)
        gr.Markdown("### Add event gallery images")
        uploads=gr.File(label="Select event images",file_count="multiple",file_types=["image"])
        add_btn=gr.Button("Add photos")
        add_status=gr.Textbox(label="Upload status",interactive=False)
        add_btn.click(add_gallery_files,inputs=uploads,outputs=add_status)
        refresh_btn=gr.Button("Refresh gallery preview")
        preview=gr.Gallery(label="Gallery preview",columns=4,height="auto")
        refresh_btn.click(preview_gallery,inputs=None,outputs=preview)
        clear_btn=gr.Button("Clear gallery",variant="stop")
        clear_status=gr.Textbox(label="Clear status",interactive=False)
        clear_btn.click(clear_gallery,inputs=None,outputs=[clear_status,preview])
        demo.load(preview_gallery,inputs=None,outputs=preview)

if __name__=="__main__":
    demo.launch()
