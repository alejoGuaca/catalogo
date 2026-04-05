import sqlite3
import os
import streamlit as st

# ── 1. Configuración de página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Catálogo de Disfraces",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "clientes.db"

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

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stRadio > label {
    font-weight: 500; letter-spacing: .04em; font-size: .85rem;
    text-transform: uppercase; color: var(--text-muted) !important; margin-bottom: .5rem;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] { background: transparent !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label {
    padding: .45rem .75rem; border-radius: 8px;
    transition: background .2s, color .2s; font-size: .9rem; letter-spacing: .02em;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label:hover {
    background: rgba(180,130,255,0.12) !important; color: var(--accent) !important;
}

/* ── Header ── */
.catalog-header { text-align: center; padding: 2.5rem 1rem 1.5rem; }
.catalog-header h1 {
    font-family: 'Cinzel Decorative', cursive;
    font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 900;
    background: linear-gradient(135deg, #f0c060 0%, #c084fc 50%, #818cf8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    letter-spacing: .04em; margin: 0 0 .4rem;
    filter: drop-shadow(0 0 18px rgba(192,132,252,0.35));
}
.catalog-header p {
    color: var(--text-muted); font-size: .95rem; font-weight: 300;
    letter-spacing: .08em; text-transform: uppercase; margin: 0;
}
.header-divider {
    width: 120px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent-gold), transparent);
    margin: 1rem auto 0; border-radius: 2px;
}

/* ── Buscador ── */
.search-wrapper { max-width: 520px; margin: 0 auto 2rem; position: relative; }
.search-wrapper .stTextInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 50px !important;
    padding: .1rem 1rem .1rem 2.8rem !important;
    color: var(--text-primary) !important;
    font-family: 'Raleway', sans-serif !important;
    font-size: .95rem !important;
    transition: border-color .25s, box-shadow .25s;
}
.search-wrapper .stTextInput > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(192,132,252,0.18) !important;
}
.search-wrapper .stTextInput input { color: var(--text-primary) !important; background: transparent !important; }
.search-wrapper .stTextInput input::placeholder { color: var(--text-muted) !important; }
.search-icon {
    position: absolute; left: 1rem; top: 50%; transform: translateY(-50%);
    color: var(--text-muted); font-size: 1rem; pointer-events: none; z-index: 10;
}

/* ── Badge categoría ── */
.category-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(192,132,252,0.18), rgba(129,140,248,0.10));
    border: 1px solid rgba(192,132,252,0.3); border-radius: 50px;
    padding: .3rem 1rem; font-size: .8rem; letter-spacing: .1em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 1.5rem; font-weight: 600;
}

/* ── Tarjeta ── */
.costume-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
    margin-bottom: 1.5rem;
    padding-bottom: .25rem;
}
.costume-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(192,132,252,0.3), 0 0 24px rgba(192,132,252,0.12);
    border-color: rgba(192,132,252,0.45);
}
.costume-card [data-testid="stImage"] { border-radius: var(--radius) var(--radius) 0 0; overflow: hidden; }
.costume-card [data-testid="stImage"] img { border-radius: var(--radius) var(--radius) 0 0; display: block; transition: transform .45s ease; }
.costume-card:hover [data-testid="stImage"] img { transform: scale(1.04); }

.costume-info { padding: .85rem 1rem .6rem; display: block !important; visibility: visible !important; }
.costume-name {
    font-family: 'Cinzel Decorative', cursive; font-size: .9rem; font-weight: 700;
    color: var(--text-primary); margin: 0 0 .4rem; letter-spacing: .02em; line-height: 1.3;
    height: 2.6em;           /* exactamente 2 líneas (line-height 1.3 × 2) */
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
}
.costume-size {
    display: inline-flex; align-items: center; gap: .35rem;
    background: rgba(240,192,96,0.1); border: 1px solid rgba(240,192,96,0.25);
    border-radius: 6px; padding: .2rem .6rem; font-size: .75rem;
    color: var(--accent-gold); font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
}

/* ── Carrusel ── */
.img-counter {
    font-size: .7rem; color: var(--text-muted); letter-spacing: .06em;
    text-align: center; padding: .3rem 0 .1rem;
}
.carousel-dots {
    display: flex; gap: 5px; align-items: center; justify-content: center;
    padding: .3rem 0 .5rem;
}
.carousel-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: rgba(192,132,252,0.25); display: inline-block;
}
.carousel-dot.active {
    background: var(--accent); width: 18px; border-radius: 3px;
}
/* Flechas del carrusel */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(192,132,252,0.1) !important;
    border: 1px solid rgba(192,132,252,0.25) !important;
    border-radius: 8px !important;
    color: var(--accent) !important;
    font-size: 1.1rem !important;
    line-height: 1 !important;
    padding: .1rem .5rem !important;
    min-height: unset !important;
    height: 2rem !important;
    width: 100% !important;
    transition: background .2s, border-color .2s !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(192,132,252,0.22) !important;
    border-color: var(--accent) !important;
}

/* ── Contadores ── */
.results-count {
    font-size: .8rem; color: var(--text-muted); letter-spacing: .06em;
    text-transform: uppercase; margin-bottom: 1.2rem; text-align: right;
}
.results-count b { color: var(--accent); }
.no-results { text-align: center; padding: 4rem 1rem; color: var(--text-muted); }
.no-results .nr-icon { font-size: 3rem; margin-bottom: 1rem; }
.no-results h3 { font-family: 'Cinzel Decorative', cursive; font-size: 1.1rem; color: var(--text-primary); margin: 0 0 .5rem; }
.no-results p { font-size: .9rem; margin: 0; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(192,132,252,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

footer { visibility: hidden; }
#MainMenu { visibility: visible; }
.stDeployButton { display: none; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Tamaño fijo de imágenes ── */
.costume-card [data-testid="stImage"] img {
    width: 100%;
    height: 320px;
    object-fit: cover;
    object-position: top center;
}
       
</style>
""", unsafe_allow_html=True)


# ── 3. Base de datos ──────────────────────────────────────────────────────────
def obtener_datos(query, params=()):
    if not os.path.exists(DB_PATH):
        st.error(f"❌ No se encontró la base de datos en: '{DB_PATH}'.")
        st.stop()
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query, params)
        datos = cur.fetchall()
        conn.close()
        return datos
    except sqlite3.Error as e:
        st.error(f"❌ Error en la base de datos: {e}")
        st.stop()


def obtener_imagenes(disfraz_id):
    """Devuelve lista de rutas válidas ordenadas para un disfraz."""
    filas = obtener_datos(
        "SELECT imagen_nombre FROM disfraz_imagenes WHERE disfraz_id = ? ORDER BY orden ASC",
        (disfraz_id,)
    )
    rutas = []
    for (nombre,) in filas:
        ruta = f"static/imagenes/{nombre}"
        if nombre and os.path.exists(ruta):
            rutas.append(ruta)
    return rutas


# ── 4. Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 0 .5rem; text-align:center;'>
        <div style='font-family:"Cinzel Decorative",cursive; font-size:1rem;
                    background:linear-gradient(135deg,#f0c060,#c084fc);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text; filter:drop-shadow(0 0 8px rgba(192,132,252,0.4));'>
            🎭 DISFRACES
        </div>
        <div style='height:1px; background:linear-gradient(90deg,transparent,rgba(192,132,252,0.4),transparent);
                    margin:.8rem 0 1.5rem;'></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:#8b7fa8; margin-bottom:.5rem;'>Categorías</p>", unsafe_allow_html=True)

    categorias_db = obtener_datos("SELECT DISTINCT categoria FROM disfraces")
    lista_categorias = [cat[0] for cat in categorias_db if cat[0]]
    lista_categorias.insert(0, "Todos")

    categoria_seleccionada = st.radio(
        label="Categorías",
        options=lista_categorias,
        label_visibility="collapsed",
    )


# ── 5. Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class='catalog-header'>
    <h1>Catálogo de Disfraces</h1>
    <p>Encuentra el disfraz perfecto para tu ocasión</p>
    <div class='header-divider'></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='search-wrapper'><span class='search-icon'>🔍</span>", unsafe_allow_html=True)
busqueda = st.text_input(
    label="buscar", placeholder="Buscar disfraz por nombre...",
    label_visibility="collapsed", key="buscador",
)
st.markdown("</div>", unsafe_allow_html=True)


# ── 6. Consulta + filtros ─────────────────────────────────────────────────────
if categoria_seleccionada == "Todos":
    disfraces = obtener_datos("SELECT id, nombre, talla FROM disfraces")
else:
    disfraces = obtener_datos(
        "SELECT id, nombre, talla FROM disfraces WHERE categoria = ?",
        (categoria_seleccionada,)
    )

if busqueda.strip():
    termino = busqueda.strip().lower()
    disfraces = [d for d in disfraces if termino in d[1].lower()]


# ── 7. Badge + contador ───────────────────────────────────────────────────────
badge_label = categoria_seleccionada if categoria_seleccionada != "Todos" else "Todos los disfraces"
st.markdown(f"""
<div style='text-align:center;'>
    <div class='category-badge'>✦ {badge_label} ✦</div>
</div>
<div class='results-count'>
    <b>{len(disfraces)}</b> disfraz{'es' if len(disfraces) != 1 else ''} encontrado{'s' if len(disfraces) != 1 else ''}
</div>
""", unsafe_allow_html=True)


# ── 8. Cuadrícula con carrusel ────────────────────────────────────────────────
if not disfraces:
    st.markdown("""
    <div class='no-results'>
        <div class='nr-icon'>🎭</div>
        <h3>Sin resultados</h3>
        <p>No encontramos disfraces que coincidan con tu búsqueda.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    cols = st.columns(3, gap="medium")

    for i, (disfraz_id, nombre, talla) in enumerate(disfraces):
        talla_texto = talla if talla else "N/A"
        imagenes    = obtener_imagenes(disfraz_id)
        total_imgs  = len(imagenes)

        # Índice del carrusel persistido en session_state
        key_idx = f"carousel_{disfraz_id}"
        if key_idx not in st.session_state:
            st.session_state[key_idx] = 0
        idx_actual = st.session_state[key_idx]

        with cols[i % 3]:
            st.markdown("<div class='costume-card'>", unsafe_allow_html=True)

            # ── Imagen actual ──
            if total_imgs > 0:
                st.image(imagenes[idx_actual], use_container_width=True)
            else:
                st.markdown("""
                <div style='background:linear-gradient(135deg,#1a1624,#110e1a);
                            padding:3.5rem 1rem; text-align:center;
                            font-size:2.5rem; color:#8b7fa8;
                            border-radius:14px 14px 0 0;'>
                    🎭<br>
                    <span style='font-size:.7rem; letter-spacing:.1em;
                                 text-transform:uppercase; font-family:Raleway,sans-serif;'>
                        Sin imagen
                    </span>
                </div>
                """, unsafe_allow_html=True)

            # ── Nombre y talla ──
            st.markdown(f"""
            <div class='costume-info'>
                <div class='costume-name'>{nombre}</div>
                <div class='costume-size'>📏 Talla: {talla_texto}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Carrusel (solo si hay más de 1 imagen) ──
            if total_imgs > 1:
                # Contador textual
                st.markdown(
                    f"<div class='img-counter'>{idx_actual + 1} / {total_imgs}</div>",
                    unsafe_allow_html=True
                )

                # Dots
                dots_html = "<div class='carousel-dots'>"
                for d in range(total_imgs):
                    cls = "carousel-dot active" if d == idx_actual else "carousel-dot"
                    dots_html += f"<span class='{cls}'></span>"
                dots_html += "</div>"
                st.markdown(dots_html, unsafe_allow_html=True)

                # Flechas
                col_prev, col_space, col_next = st.columns([1, 4, 1])
                with col_prev:
                    if st.button("‹", key=f"prev_{disfraz_id}"):
                        st.session_state[key_idx] = (idx_actual - 1) % total_imgs
                        st.rerun()
                with col_next:
                    if st.button("›", key=f"next_{disfraz_id}"):
                        st.session_state[key_idx] = (idx_actual + 1) % total_imgs
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# Ejecutar con:
# python -m streamlit run catalogo.py
# ctl + c para detener el servidor