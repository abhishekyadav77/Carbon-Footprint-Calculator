import os
import base64
import pickle
import re
import warnings

import numpy as np
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

from functions import *  # noqa: F401,F403  (click_element, sample, input_preprocessing, chart, BASE_DIR)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


st.set_page_config(
    layout="wide",
    page_title="Carbon Footprint Calculator",
    page_icon=os.path.join(BASE_DIR, "media", "favicon.ico"),
    initial_sidebar_state="collapsed",
)

def get_base64(bin_file):
    with open(os.path.join(BASE_DIR, bin_file), 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

background = get_base64("./media/background_min.jpg")
icon2 = get_base64("./media/icon2.png")
icon3 = get_base64("./media/icon3.png")

with open(os.path.join(BASE_DIR, "style", "style.css"), "r", encoding="utf-8") as style:
    css = style.read()


css = css.replace("{background}", background)
css = css.replace("{icon2}", icon2)
css = css.replace("{icon3}", icon3)

css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
css = "\n".join(line for line in css.splitlines() if line.strip())

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def script():
    with open(os.path.join(BASE_DIR, "style", "scripts.js"), "r", encoding="utf-8") as scripts:
        open_script = f"""<script>{scripts.read()}</script> """
        html(open_script, width=0, height=0)


def go_to_first_page(outer_tab):
    """Open the outer tab (`tab-0` = Home, `tab-1` = Form) AND force the inner form to its first page (Personal)."""
    st.session_state.nav_n = st.session_state.get("nav_n", 0) + 1
    html(
        f"""<script>
        // nav #{st.session_state.nav_n}
        (function () {{
            var doc = window.parent.document;
            var outer = doc.querySelector('[id^=tabs-bui][id$=-{outer_tab}]');
            if (outer) {{ outer.click(); }}
            function openFirst() {{
                var lists = Array.from(doc.querySelectorAll('[data-baseweb="tab-list"]'));
                var form = lists.find(function (l) {{
                    return l.querySelectorAll('button[data-baseweb="tab"]').length === 5;
                }});
                if (!form) {{ return; }}
                var first = form.querySelector('button[data-baseweb="tab"]');
                if (first && first.getAttribute('aria-selected') !== 'true') {{ first.click(); }}
            }}
            [50, 250, 600].forEach(function (ms) {{ setTimeout(openFirst, ms); }});
            window.parent.scrollTo({{top: 0, behavior: 'smooth'}});
        }})();
        </script>""",
        width=0,
        height=0,
    )


left, middle, right = st.columns([1.3, 3.8, 1.3])
main, comps, result = middle.tabs([" ", " ", " "])

with open(os.path.join(BASE_DIR, "style", "main.md"), "r", encoding="utf-8") as main_page:
    main.markdown(f"""{main_page.read()}""")

if main.button("Calculate Your Carbon Footprint!", type="primary"):
    go_to_first_page('tab-1')

tab1, tab2, tab3, tab4, tab5 = comps.tabs(["👴 Personal", "🚗 Travel", "🗑️ Waste", "⚡ Energy", "💸 Consumption"])
tab_result, _ = result.tabs([" ", " "])

# ---- Reset support: every form widget gets a key that contains `form_v`.
# Bumping form_v gives all widgets brand-new keys, so they come back with default values.
if "form_v" not in st.session_state:
    st.session_state.form_v = 0
if "go_first_page" not in st.session_state:
    st.session_state.go_first_page = False


def reset_form():
    st.session_state.form_v += 1
    st.session_state.go_first_page = True


def component():
    v = st.session_state.form_v
    tab1col1, tab1col2 = tab1.columns(2)
    height = tab1col1.number_input("Height", 0, 251, value=None, placeholder="160", help="in cm", key=f"height_{v}")
    weight = tab1col2.number_input("Weight", 0, 250, value=None, placeholder="75", help="in kg", key=f"weight_{v}")
    if not height or not weight:
        # Height/weight not filled in yet -> use a neutral default instead of a fake BMI of 10000
        body_type = "normal"
    else:
        calculation = weight / (height / 100) ** 2
        body_type = "underweight" if (calculation < 18.5) else \
                    "normal" if ((calculation >= 18.5) and (calculation < 25)) else \
                    "overweight" if ((calculation >= 25) and (calculation < 30)) else "obese"
    sex = tab1.selectbox('Gender', ["female", "male"], key=f"sex_{v}")
    diet = tab1.selectbox(
        'Diet',
        ['omnivore', 'pescatarian', 'vegetarian', 'vegan'],
        help="""
        Omnivore: Eats both plants and animals.\n
        Pescatarian: Consumes plants and seafood, but no other meat\n
        Vegetarian: Diet excludes meat but includes plant-based foods.\n
        Vegan: Avoids all animal products, including meat, dairy, and eggs.
        """,
        key=f"diet_{v}"
    )
    social = tab1.selectbox('Social Activity', ['never', 'often', 'sometimes'], help="How often do you go out?", key=f"social_{v}")

    transport = tab2.selectbox(
        'Transportation',
        ['public', 'private', 'walk/bicycle'],
        help="Which transportation method do you prefer the most?",
        key=f"transport_{v}"
    )
    if transport == "private":
        vehicle_type = tab2.selectbox(
            'Vehicle Type',
            ['petrol', 'diesel', 'hybrid', 'lpg', 'electric'],
            help="What type of fuel do you use in your car?",
            key=f"vehicle_type_{v}"
        )
    else:
        vehicle_type = "None"

    if transport == "walk/bicycle":
        vehicle_km = 0
    else:
        vehicle_km = tab2.slider(
            'What is the monthly distance traveled by the vehicle in kilometers?',
            0, 5000, 0, disabled=False, key=f"vehicle_km_{v}"
        )

    air_travel = tab2.selectbox(
        'How often did you fly last month?',
        ['never', 'rarely', 'frequently', 'very frequently'],
        help="""
        Never: I didn't travel by plane.\n
        Rarely: Around 1-4 Hours.\n
        Frequently: Around 5 - 10 Hours.\n
        Very Frequently: Around 10+ Hours.
        """,
        key=f"air_travel_{v}"
    )

    waste_bag = tab3.selectbox('What is the size of your waste bag?', ['small', 'medium', 'large', 'extra large'], key=f"waste_bag_{v}")
    waste_count = tab3.slider('How many waste bags do you trash out in a week?', 0, 10, 0, key=f"waste_count_{v}")
    recycle = tab3.multiselect('Do you recycle any materials below?', ['Plastic', 'Paper', 'Metal', 'Glass'], key=f"recycle_{v}")

    heating_energy = tab4.selectbox(
        'What power source do you use for heating?',
        ['natural gas', 'electricity', 'wood', 'coal'],
        key=f"heating_energy_{v}"
    )

    for_cooking = tab4.multiselect(
        'What cooking systems do you use?',
        ['microwave', 'oven', 'grill', 'airfryer', 'stove'],
        key=f"for_cooking_{v}"
    )
    energy_efficiency = tab4.selectbox(
        'Do you consider the energy efficiency of electronic devices?',
        ['No', 'Yes', 'Sometimes'],
        key=f"energy_efficiency_{v}"
    )
    daily_tv_pc = tab4.slider('How many hours a day do you spend in front of your PC/TV?', 0, 24, 0, key=f"daily_tv_pc_{v}")
    internet_daily = tab4.slider('What is your daily internet usage in hours?', 0, 24, 0, key=f"internet_daily_{v}")

    shower = tab5.selectbox(
        'How often do you take a shower?',
        ['daily', 'twice a day', 'more frequently', 'less frequently'],
        key=f"shower_{v}"
    )
    grocery_bill = tab5.slider('Monthly grocery spending in ₹', 0, 5000, 0, key=f"grocery_bill_{v}")
    clothes_monthly = tab5.slider('How many clothes do you buy monthly?', 0, 30, 0, key=f"clothes_monthly_{v}")

    data = {
        'Body Type': body_type,
        "Sex": sex,
        'Diet': diet,
        "How Often Shower": shower,
        "Heating Energy Source": heating_energy,
        "Transport": transport,
        "Social Activity": social,
        'Monthly Grocery Bill': grocery_bill,
        "Frequency of Traveling by Air": air_travel,
        "Vehicle Monthly Distance Km": vehicle_km,
        "Waste Bag Size": waste_bag,
        "Waste Bag Weekly Count": waste_count,
        "How Long TV PC Daily Hour": daily_tv_pc,
        "Vehicle Type": vehicle_type,
        "How Many New Clothes Monthly": clothes_monthly,
        "How Long Internet Daily Hour": internet_daily,
        "Energy efficiency": energy_efficiency
    }

    data.update({
        f"Cooking_with_{x}": y
        for x, y in dict(zip(for_cooking, np.ones(len(for_cooking)))).items()
    })
    data.update({
        f"Do You Recyle_{x}": y
        for x, y in dict(zip(recycle, np.ones(len(recycle)))).items()
    })

    return pd.DataFrame(data, index=[0])

df = component()
data = input_preprocessing(df)

sample_df = pd.DataFrame(data=sample, index=[0])
sample_df[sample_df.columns] = 0
sample_df[data.columns] = data

@st.cache_resource
def load_models():
    with open(os.path.join(BASE_DIR, "models", "scale.sav"), "rb") as f:
        scaler = pickle.load(f)
    with open(os.path.join(BASE_DIR, "models", "model.sav"), "rb") as f:
        mdl = pickle.load(f)
    return scaler, mdl


ss, model = load_models()
prediction = round(np.exp(model.predict(ss.transform(sample_df))[0]))

# ---- Back / Next navigation at the bottom of every form tab ----
# Keys are required: the same label is used in several tabs.
_, nav1_next = tab1.columns(2)
go_next = {0: nav1_next.button("Next →", key="next_0", type="primary")}

go_back = {}
for _i, _tab in ((1, tab2), (2, tab3), (3, tab4)):
    _back_col, _next_col = _tab.columns(2)
    go_back[_i] = _back_col.button("← Back", key=f"back_{_i}", type="secondary")
    go_next[_i] = _next_col.button("Next →", key=f"next_{_i}", type="primary")

_back_col, _submit_col = tab5.columns(2)
go_back[4] = _back_col.button("← Back", key="back_4", type="secondary")
submitted = _submit_col.button("See My Footprint", type="primary")

for _i, _clicked in go_next.items():
    if _clicked:
        click_inner_tab(_i + 1)
for _i, _clicked in go_back.items():
    if _clicked:
        click_inner_tab(_i - 1)

# "Did you know" fact box + Home button (the text of the facts lives in scripts.js)
tab_dyk = comps.container()
tab_dyk.markdown(
    """
<div class="dyk-wrap">
  <button id="dyk-btn" class="pill-btn pill-btn--secondary" type="button">❔ Did You Know?</button>
</div>
<div id="popup" role="note" title="Click to close">
  <p class="dyk-title">❔ Did you know?</p>
  <p id="popupText" class="dyk-content">Each year, human activities release over 40 billion tonnes of CO₂ into the atmosphere.</p>
  <p class="dyk-hint">Click this box to close it.</p>
</div>
""",
    unsafe_allow_html=True,
)

if comps.button("🏡 Home", type="secondary"):
    go_to_first_page('tab-0')

if submitted:
    tree_count = round(prediction / 411.4)

    tab_result.markdown(
        f"""
<div class="result-hero">
  <p class="result-eyebrow">Your monthly carbon footprint</p>
  <p class="result-value">{prediction:,}</p>
  <p class="result-unit">kg CO₂e per month</p>
</div>
""",
        unsafe_allow_html=True,
    )
    tab_result.image(chart(model, ss, sample_df, prediction), use_column_width=True)

    tab_result.caption(
        "**Note:** This result is only an approximate estimate generated by our machine-learning model. "
        "It should not be considered an exact measurement of your actual carbon footprint. "
        "The model is trained on a general dataset, so the results may vary depending on individual lifestyle and usage patterns. "
        "The chart represents an estimated contribution of each category to your overall footprint."
    )

    if tree_count > 0:
        tab_result.markdown(
            f"""
<div class="result-tree">
  <p>🌳 To offset your emissions, plant <b>{tree_count}</b> tree{'s' if tree_count > 1 else ''} every month.</p>
  <a class="pill-btn pill-btn--secondary" href="https://www.un.org/en/actnow/ten-actions" target="_blank" rel="noopener noreferrer">Methods to Reduce Emissions</a>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        tab_result.markdown(
            """
<div class="result-tree">
  <p>🌿 Great job! Your monthly emission is very low - no extra trees needed.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    click_element('tab-2')

# lives outside the `if submitted` block on purpose: a button created inside it
# would disappear on the rerun that its own click triggers
result.button("Calculate Again", type="primary", on_click=reset_form)

# After "Calculate Again": open the form tab on its FIRST page (Personal).
if st.session_state.go_first_page:
    st.session_state.go_first_page = False
    go_to_first_page('tab-1')

with open(os.path.join(BASE_DIR, "style", "footer.html"), "r", encoding="utf-8") as footer:
    footer_html = f"""{footer.read()}"""
    st.markdown(footer_html, unsafe_allow_html=True)

script()