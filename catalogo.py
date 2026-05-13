import psycopg2
import os
import streamlit as st
import streamlit.components.v1 as components

# --- REEMPLAZA ESTA URL POR LA TUYA DE SUPABASE ---
DATABASE_URL = "postgresql://postgres.mcluogcayzabrosunjth:Familia#99Share@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

# ── 1. Configuración de página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Catálogo de Disfraces",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. CSS global ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Raleway:wght@300;400;500;600&display=swap');

:root {
    --bg-deep:      #0a090f;
    --bg-card:      #13111a;
    --bg-sidebar:   #0e0d14;
    --border:       rgba(180,130,255,0.18);
    --accent:       #c084fc;
    --accent-glow:  #a855f7;
    --accent-gold:  #f0c060;
    --text-primary: #ede8f5;
    --text-muted:   #8b7fa8;
    --radius:       14px;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: 'Raleway', sans-serif !important;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(168,85,247,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(192,132,252,0.08) 0%, transparent 55%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] { background: var(--bg-sidebar) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stRadio > label { font-weight: 500; letter-spacing: .04em; font-size: .85rem; text-transform: uppercase; color: var(--text-muted) !important; margin-bottom: .5rem; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] { background: transparent !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label { padding: .45rem .75rem; border-radius: 8px; transition: background .2s, color .2s; font-size: .9rem; letter-spacing: .02em; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label:hover { background: rgba(180,130,255,0.12) !important; color: var(--accent) !important; }

.catalog-header { text-align: center; padding: 2.5rem 1rem 1.5rem; }
.catalog-header h1 { font-family: 'Cinzel Decorative', cursive; font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 900; background: linear-gradient(135deg, #f0c060 0%, #c084fc 50%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: .04em; margin: 0 0 .4rem; filter: drop-shadow(0 0 18px rgba(192,132,252,0.35)); }
.catalog-header p { color: var(--text-muted); font-size: .95rem; font-weight: 300; letter-spacing: .08em; text-transform: uppercase; margin: 0; }
.header-divider { width: 120px; height: 2px; background: linear-gradient(90deg, transparent, var(--accent), var(--accent-gold), transparent); margin: 1rem auto 0; border-radius: 2px; }

.search-wrapper { max-width: 520px; margin: 0 auto 2rem; position: relative; }
.search-wrapper .stTextInput > div > div { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--border) !important; border-radius: 50px !important; padding: .1rem 1rem .1rem 2.8rem !important; color: var(--text-primary) !important; font-family: 'Raleway', sans-serif !important; font-size: .95rem !important; transition: border-color .25s, box-shadow .25s; }
.search-wrapper .stTextInput > div > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(192,132,252,0.18) !important; }
.search-wrapper .stTextInput input { color: var(--text-primary) !important; background: transparent !important; }
.search-wrapper .stTextInput input::placeholder { color: var(--text-muted) !important; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 1rem; pointer-events: none; z-index: 10; }

.category-badge { display: inline-block; background: linear-gradient(135deg, rgba(192,132,252,0.18), rgba(129,140,248,0.10)); border: 1px solid rgba(192,132,252,0.3); border-radius: 50px; padding: .3rem 1rem; font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.5rem; font-weight: 600; }

.results-count { font-size: .8rem; color: var(--text-muted); letter-spacing: .06em; text-transform: uppercase; margin-bottom: 1.2rem; text-align: right; }
.results-count b { color: var(--accent); }
.no-results { text-align: center; padding: 4rem 1rem; color: var(--text-muted); }
.no-results .nr-icon { font-size: 3rem; margin-bottom: 1rem; }
.no-results h3 { font-family: 'Cinzel Decorative', cursive; font-size: 1.1rem; color: var(--text-primary); margin: 0 0 .5rem; }
.no-results p { font-size: .9rem; margin: 0; }

.detail-back-btn { display: inline-flex; align-items: center; gap: .5rem; background: rgba(192,132,252,0.1); border: 1px solid rgba(192,132,252,0.3); border-radius: 50px; padding: .5rem 1.2rem; color: var(--accent); font-size: .85rem; letter-spacing: .05em; text-decoration: none; cursor: pointer; margin-bottom: 2rem; transition: background .2s, border-color .2s; }
.detail-back-btn:hover { background: rgba(192,132,252,0.2); border-color: var(--accent); }
.detail-name { font-family: 'Cinzel Decorative', cursive; font-size: clamp(1.4rem, 3vw, 2.2rem); font-weight: 900; background: linear-gradient(135deg, #f0c060 0%, #c084fc 50%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0 0 1rem; }
.detail-size-badge { display: inline-flex; align-items: center; gap: .4rem; background: rgba(240,192,96,0.10); border: 1px solid rgba(240,192,96,0.28); border-radius: 8px; padding: .4rem .9rem; font-size: .85rem; color: #f0c060; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 1.5rem; }

.share-box { background: rgba(192,132,252,0.06); border: 1px solid rgba(192,132,252,0.25); border-radius: 12px; padding: 1.2rem 1.4rem; margin-top: 1.5rem; }
.share-box h4 { font-family: 'Cinzel Decorative', cursive; font-size: .8rem; color: var(--accent); letter-spacing: .1em; text-transform: uppercase; margin: 0 0 .8rem; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(192,132,252,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
footer { visibility: hidden; } #MainMenu { visibility: visible; } .stDeployButton { display: none; } [data-testid="stDecoration"] { display: none !important; } iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)


# ── 3. Base de datos PostgreSQL ───────────────────────────────────────────────
def obtener_datos(query, params=()):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(query, params)
        datos = cur.fetchall()
        conn.close()
        return datos
    except psycopg2.Error as e:
        st.error(f"❌ Error en la base de datos (Supabase): {e}")
        st.stop()


def obtener_imagenes(disfraz_id):
    filas = obtener_datos(
        "SELECT imagen_nombre FROM disfraz_imagenes WHERE disfraz_id = %s ORDER BY orden ASC",
        (disfraz_id,)
    )
    rutas =[]
    for (nombre,) in filas:
        ruta = f"static/imagenes/{nombre}"
        if nombre and os.path.exists(ruta):
            rutas.append(ruta)
    return rutas


def imagen_a_base64(ruta):
    import base64, mimetypes
    mime, _ = mimetypes.guess_type(ruta)
    mime = mime or "image/jpeg"
    with open(ruta, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"

# HTML functions unchanged...
def tarjeta_html(nombre, talla_texto, imagenes, card_height=400):
    imgs_b64 =[]
    for ruta in imagenes:
        try: imgs_b64.append(imagen_a_base64(ruta))
        except: pass
    total = len(imgs_b64)
    imgs_js = "[" + ",".join(f'"{u}"' for u in imgs_b64) + "]"
    img_html = '<img class="slide-img" id="mainImg" src="" alt="disfraz">' if total > 0 else '<div class="no-img"><span>🎭</span>Sin imagen</div>'
    controles_html = '<button class="arrow left" onclick="cambiar(-1)">&#8249;</button><button class="arrow right" onclick="cambiar(1)">&#8250;</button><div class="dots" id="dots"></div>' if total > 1 else ""

    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Raleway:wght@400;500;600&display=swap'); * {{ box-sizing: border-box; margin: 0; padding: 0; }} body {{ background: #13111a; font-family: 'Raleway', sans-serif; padding: 2px; }} .card {{ background: #13111a; border: 1px solid rgba(180,130,255,0.18); border-radius: 14px; overflow: hidden; transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease; }} .card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(192,132,252,0.3), 0 0 24px rgba(192,132,252,0.12); border-color: rgba(192,132,252,0.45); }} .img-zone {{ position: relative; width: 100%; height: {card_height}px; overflow: hidden; background: linear-gradient(135deg, #1a1624, #110e1a); }} .slide-img {{ width: 100%; height: 100%; object-fit: contain; object-position: center; display: block; transition: transform .45s ease; user-select: none; -webkit-user-drag: none; pointer-events: none; }} .card:hover .slide-img {{ transform: scale(1.04); }} .no-img {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #8b7fa8; font-size: .75rem; letter-spacing: .1em; text-transform: uppercase; gap: .6rem; }} .no-img span {{ font-size: 2.5rem; }} .arrow {{ position: absolute; top: 50%; transform: translateY(-50%); z-index: 30; width: 36px; height: 36px; border-radius: 50%; border: 1px solid rgba(192,132,252,0.4); background: rgba(10,9,15,0.60); color: #c084fc; font-size: 1.4rem; line-height: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); opacity: 0; transition: opacity .2s, background .2s, transform .15s; -webkit-tap-highlight-color: transparent; touch-action: manipulation; }} .arrow.left {{ left: 10px; }} .arrow.right {{ right: 10px; }} .img-zone:hover .arrow {{ opacity: 1; }} .arrow:hover {{ background: rgba(192,132,252,0.28); border-color: #c084fc; }} .arrow:active {{ transform: translateY(-50%) scale(0.9); }} @media (hover: none) {{ .arrow {{ opacity: 0.80; }} }} .dots {{ position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); z-index: 30; display: flex; gap: 5px; align-items: center; background: rgba(10,9,15,0.45); padding: 5px 10px; border-radius: 20px; backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); pointer-events: none; }} .dot {{ width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.40); transition: all .25s; display: inline-block; }} .dot.active {{ background: #c084fc; width: 16px; border-radius: 3px; }} .info {{ padding: .85rem 1rem .75rem; }} .costume-name {{ font-family: 'Cinzel Decorative', cursive; font-size: .85rem; font-weight: 700; color: #ede8f5; margin: 0 0 .5rem; letter-spacing: .02em; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.3em; }} .costume-size {{ display: inline-flex; align-items: center; gap: .35rem; background: rgba(240,192,96,0.10); border: 1px solid rgba(240,192,96,0.28); border-radius: 6px; padding: .22rem .65rem; font-size: .72rem; color: #f0c060; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; }}</style></head><body><div class="card"><div class="img-zone" id="zone">{img_html}{controles_html}</div><div class="info"><div class="costume-name">{nombre}</div><div class="costume-size">📏 Talla: {talla_texto}</div></div></div><script>(function() {{ var imgs={imgs_js}; var total=imgs.length; var cur=0; var startX=0; function setImg() {{ if(total===0) return; document.getElementById('mainImg').src=imgs[cur]; }} function setDots() {{ if(total<=1) return; var d=document.getElementById('dots'); d.innerHTML=''; for(var i=0;i<total;i++){{ var s=document.createElement('span'); s.className='dot'+(i===cur?' active':''); d.appendChild(s); }} }} window.cambiar=function(dir){{ cur=(cur+dir+total)%total; setImg(); setDots(); }}; var zone=document.getElementById('zone'); zone.addEventListener('touchstart',function(e){{ startX=e.changedTouches[0].clientX; }},{{passive:true}}); zone.addEventListener('touchend',function(e){{ var dx=e.changedTouches[0].clientX-startX; if(Math.abs(dx)>40) window.cambiar(dx<0?1:-1); }},{{passive:true}}); setImg(); setDots(); }})();</script></body></html>"""

def carrusel_detalle_html(imagenes, altura=520):
    imgs_b64 =[]
    for ruta in imagenes:
        try: imgs_b64.append(imagen_a_base64(ruta))
        except: pass
    total = len(imgs_b64)
    imgs_js = "[" + ",".join(f'"{u}"' for u in imgs_b64) + "]"
    if total == 0: return f"""<div style="height:{altura}px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1a1624,#110e1a);border-radius:16px;color:#8b7fa8;font-size:3rem;">🎭</div>"""
    controles = '<button class="arrow left" onclick="cambiar(-1)">&#8249;</button><button class="arrow right" onclick="cambiar(1)">&#8250;</button><div class="dots" id="dots"></div><div class="counter" id="counter"></div>' if total > 1 else ""
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>* {{ box-sizing:border-box; margin:0; padding:0; }} body {{ background:#0a090f; font-family:sans-serif; }} .zone {{ position:relative; width:100%; height:{altura}px; overflow:hidden; background:linear-gradient(135deg,#1a1624,#110e1a); border-radius:16px; border:1px solid rgba(180,130,255,0.2); }} .slide-img {{ width:100%; height:100%; object-fit:contain; object-position:center; display:block; user-select:none; -webkit-user-drag:none; pointer-events:none; }} .arrow {{ position:absolute; top:50%; transform:translateY(-50%); z-index:30; width:46px; height:46px; border-radius:50%; border:1px solid rgba(192,132,252,0.5); background:rgba(10,9,15,0.7); color:#c084fc; font-size:1.8rem; display:flex; align-items:center; justify-content:center; cursor:pointer; backdrop-filter:blur(6px); transition:background .2s; -webkit-tap-highlight-color:transparent; touch-action:manipulation; }} .arrow.left {{ left:14px; }} .arrow.right {{ right:14px; }} .arrow:hover {{ background:rgba(192,132,252,0.3); }} .arrow:active {{ transform:translateY(-50%) scale(0.9); }} .dots {{ position:absolute; bottom:14px; left:50%; transform:translateX(-50%); z-index:30; display:flex; gap:6px; align-items:center; background:rgba(10,9,15,0.5); padding:6px 12px; border-radius:20px; backdrop-filter:blur(4px); pointer-events:none; }} .dot {{ width:7px; height:7px; border-radius:50%; background:rgba(255,255,255,0.35); transition:all .25s; }} .dot.active {{ background:#c084fc; width:20px; border-radius:4px; }} .counter {{ position:absolute; top:14px; right:14px; background:rgba(10,9,15,0.55); color:#c084fc; font-size:.75rem; padding:4px 10px; border-radius:20px; backdrop-filter:blur(4px); letter-spacing:.06em; }} @media (hover:none) {{ .arrow {{ opacity:0.85; }} }}</style></head><body><div class="zone" id="zone"><img class="slide-img" id="mainImg" src="" alt="disfraz">{controles}</div><script>(function() {{ var imgs={imgs_js}; var total=imgs.length; var cur=0; var startX=0; function update() {{ document.getElementById('mainImg').src=imgs[cur]; if(total>1) {{ var d=document.getElementById('dots'); d.innerHTML=''; for(var i=0;i<total;i++) {{ var s=document.createElement('span'); s.className='dot'+(i===cur?' active':''); d.appendChild(s); }} document.getElementById('counter').textContent=(cur+1)+'/'+total; }} }} window.cambiar=function(dir){{ cur=(cur+dir+total)%total; update(); }}; var z=document.getElementById('zone'); z.addEventListener('touchstart',function(e){{ startX=e.changedTouches[0].clientX; }},{{passive:true}}); z.addEventListener('touchend',function(e){{ var dx=e.changedTouches[0].clientX-startX; if(Math.abs(dx)>40) window.cambiar(dx<0?1:-1); }},{{passive:true}}); update(); }})();</script></body></html>"""

# ── 4. Leer query params ───────────────────────────────────────────────────────
params = st.query_params
disfraz_id_param = params.get("disfraz", None)

if disfraz_id_param:
    try: disfraz_id_param = int(disfraz_id_param)
    except: st.error("ID inválido."); st.stop()

    filas = obtener_datos("""
        SELECT d.id, d.nombre, d.talla, d.categoria 
        FROM disfraces d INNER JOIN disfraz_imagenes di ON di.disfraz_id = d.id 
        WHERE d.id = %s LIMIT 1
    """, (disfraz_id_param,))

    if not filas:
        st.error("No se encontró el disfraz o no tiene imágenes disponibles.")
        if st.button("← Volver al catálogo"): st.query_params.clear(); st.rerun()
        st.stop()

    did, nombre, talla, categoria = filas[0]
    imagenes = obtener_imagenes(did)
    talla_texto = talla if talla else "N/A"

    try:
        base_url = st.context.headers.get("host", "tu-app.streamlit.app")
        protocolo = "https" if "streamlit.app" in base_url else "http"
        url_directa = f"{protocolo}://{base_url}/?disfraz={did}"
    except: url_directa = f"/?disfraz={did}"

    st.markdown("""<style>div[data-testid="stButton"] > button[kind="secondary"] { background: rgba(192,132,252,0.12) !important; border: 1px solid rgba(192,132,252,0.4) !important; color: #c084fc !important; border-radius: 50px !important; font-size: .9rem !important; letter-spacing: .05em !important; padding: .55rem 1.4rem !important; } div[data-testid="stButton"] > button[kind="secondary"]:hover { background: rgba(192,132,252,0.25) !important; border-color: #c084fc !important; }</style>""", unsafe_allow_html=True)

    if st.button("← Volver al catálogo", type="secondary"): st.query_params.clear(); st.rerun()

    st.markdown(f"<div class='catalog-header' style='padding-top:.5rem;'><p style='margin-bottom:.5rem;'>{categoria or ''}</p><div class='header-divider'></div></div>", unsafe_allow_html=True)
    col_img, col_info = st.columns([3, 2], gap="large")

    with col_img:
        components.html(carrusel_detalle_html(imagenes, altura=520), height=540, scrolling=False)

    with col_info:
        st.markdown(f"<div class='detail-name'>{nombre}</div><div class='detail-size-badge'>📏 Talla: {talla_texto}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='share-box'><h4>🔗 Compartir este disfraz</h4><p style='color:#8b7fa8; font-size:.8rem; margin-bottom:.8rem;'>Copia este link y envíalo directamente a tu cliente:</p><div style='display:flex; align-items:center; gap:.5rem;'><code style='flex:1; background:rgba(10,9,15,0.6); border:1px solid rgba(180,130,255,0.2); border-radius:8px; padding:.5rem .8rem; color:#c084fc; font-size:.8rem; word-break:break-all;'>{url_directa}</code></div></div>", unsafe_allow_html=True)
        st.code(url_directa, language=None)
        st.markdown("<p style='color:#8b7fa8; font-size:.72rem; margin-top:.4rem; letter-spacing:.04em;'>💡 Selecciona el texto de arriba y cópialo con Ctrl+C / Cmd+C</p>", unsafe_allow_html=True)
    st.stop()


# ── Vista Catálogo Principal ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='padding:1.2rem 0 .5rem; text-align:center;'><div style='font-family:"Cinzel Decorative",cursive; font-size:1rem; background:linear-gradient(135deg,#f0c060,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; filter:drop-shadow(0 0 8px rgba(192,132,252,0.4));'>🎭 DISFRACES</div><div style='height:1px; background:linear-gradient(90deg,transparent,rgba(192,132,252,0.4),transparent); margin:.8rem 0 1.5rem;'></div></div><p style='font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:#8b7fa8; margin-bottom:.5rem;'>Categorías</p>""", unsafe_allow_html=True)
    
    categorias_db = obtener_datos("""
        SELECT DISTINCT d.categoria FROM disfraces d 
        INNER JOIN disfraz_imagenes di ON di.disfraz_id = d.id 
        WHERE d.categoria != '' ORDER BY d.categoria ASC
    """)
    lista_categorias = [cat[0] for cat in categorias_db if cat[0]]
    lista_categorias.insert(0, "Todos")
    categoria_seleccionada = st.radio("Categorías", options=lista_categorias, label_visibility="collapsed")


st.markdown("<div class='catalog-header'><h1>Catálogo de Disfraces</h1><p>Encuentra el disfraz perfecto para tu ocasión</p><div class='header-divider'></div></div>", unsafe_allow_html=True)
st.markdown("<div class='search-wrapper'><span class='search-icon'>🔍</span>", unsafe_allow_html=True)
busqueda = st.text_input("buscar", placeholder="Buscar disfraz por nombre...", label_visibility="collapsed", key="buscador")
st.markdown("</div>", unsafe_allow_html=True)

if categoria_seleccionada == "Todos":
    disfraces = obtener_datos("""
        SELECT DISTINCT d.id, d.nombre, d.talla FROM disfraces d 
        INNER JOIN disfraz_imagenes di ON di.disfraz_id = d.id ORDER BY d.nombre ASC
    """)
else:
    disfraces = obtener_datos("""
        SELECT DISTINCT d.id, d.nombre, d.talla FROM disfraces d 
        INNER JOIN disfraz_imagenes di ON di.disfraz_id = d.id 
        WHERE d.categoria = %s ORDER BY d.nombre ASC
    """, (categoria_seleccionada,))

if busqueda.strip():
    termino = busqueda.strip().lower()
    disfraces = [d for d in disfraces if termino in d[1].lower()]

badge_label = categoria_seleccionada if categoria_seleccionada != "Todos" else "Todos los disfraces"
st.markdown(f"<div style='text-align:center;'><div class='category-badge'>✦ {badge_label} ✦</div></div><div class='results-count'><b>{len(disfraces)}</b> disfraz{'es' if len(disfraces) != 1 else ''} encontrado{'s' if len(disfraces) != 1 else ''}</div>", unsafe_allow_html=True)

if not disfraces:
    st.markdown("<div class='no-results'><div class='nr-icon'>🎭</div><h3>Sin resultados</h3><p>No encontramos disfraces que coincidan con tu búsqueda.</p></div>", unsafe_allow_html=True)
else:
    cols = st.columns(3, gap="medium")
    for i, (disfraz_id, nombre, talla) in enumerate(disfraces):
        talla_texto = talla if talla else "N/A"
        imagenes    = obtener_imagenes(disfraz_id)
        with cols[i % 3]:
            components.html(tarjeta_html(nombre, talla_texto, imagenes, card_height=400), height=515, scrolling=False)
            if st.button(f"🔗 Ver & Compartir", key=f"share_{disfraz_id}", use_container_width=True):
                st.query_params["disfraz"] = str(disfraz_id)
                st.rerun()