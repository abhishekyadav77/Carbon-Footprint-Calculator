import io
import os

import matplotlib
matplotlib.use("Agg")  # no GUI backend needed inside Streamlit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from streamlit.components.v1 import html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def click_element(element):
    open_script = f"<script type = 'text/javascript'>window.parent.document.querySelector('[id^=tabs-bui][id$=-{element}]').click();</script>"
    html(open_script, width=0, height=0)


def click_inner_tab(index):
    """Switch the 5-tab form (Personal, Travel, Waste, Energy, Consumption) to tab `index`.

    click_element() can't be used for this: it always hits the first tab bar in the page
    (the hidden Home/Form/Result switcher). Here we find the tab bar that has 5 tabs.
    """
    script = f"""<script>
    (function () {{
        var doc = window.parent.document;
        var lists = Array.from(doc.querySelectorAll('[data-baseweb="tab-list"]'));
        var form = lists.find(function (l) {{ return l.querySelectorAll('button[data-baseweb="tab"]').length === 5; }});
        if (!form) {{ return; }}
        var tabs = form.querySelectorAll('button[data-baseweb="tab"]');
        if (tabs[{index}]) {{ tabs[{index}].click(); }}
        form.scrollIntoView({{behavior: 'smooth', block: 'center'}});
    }})();
    </script>"""
    html(script, width=0, height=0)


sample = {'Body Type': 2,
 'Sex': 0,
 'How Often Shower': 1,
 'Social Activity': 2,
 'Monthly Grocery Bill': 230,
 'Frequency of Traveling by Air': 2,
 'Vehicle Monthly Distance Km': 210,
 'Waste Bag Size': 2,
 'Waste Bag Weekly Count': 4,
 'How Long TV PC Daily Hour': 7,
 'How Many New Clothes Monthly': 26,
 'How Long Internet Daily Hour': 1,
 'Energy efficiency': 0,
 'Do You Recyle_Paper': 0,
 'Do You Recyle_Plastic': 0,
 'Do You Recyle_Glass': 0,
 'Do You Recyle_Metal': 1,
 'Cooking_with_stove': 1,
 'Cooking_with_oven': 1,
 'Cooking_with_microwave': 0,
 'Cooking_with_grill': 0,
 'Cooking_with_airfryer': 1,
 'Diet_omnivore': 0,
 'Diet_pescatarian': 1,
 'Diet_vegan': 0,
 'Diet_vegetarian': 0,
 'Heating Energy Source_coal': 1,
 'Heating Energy Source_electricity': 0,
 'Heating Energy Source_natural gas': 0,
 'Heating Energy Source_wood': 0,
 'Transport_private': 0,
 'Transport_public': 1,
 'Transport_walk/bicycle': 0,
 'Vehicle Type_None': 1,
 'Vehicle Type_diesel': 0,
 'Vehicle Type_electric': 0,
 'Vehicle Type_hybrid': 0,
 'Vehicle Type_lpg': 0,
 'Vehicle Type_petrol': 0}

def input_preprocessing(data):
    data["Body Type"] = data["Body Type"].map({'underweight':0, 'normal':1, 'overweight':2, 'obese':3})
    data["Sex"] = data["Sex"].map({'female':0, 'male':1})
    data = pd.get_dummies(data, columns=["Diet","Heating Energy Source","Transport","Vehicle Type"], dtype=int)
    data["How Often Shower"] = data["How Often Shower"].map({'less frequently':0, 'daily':1, "twice a day":2, "more frequently":3})
    data["Social Activity"] = data["Social Activity"].map({'never':0, 'sometimes':1, "often":2})
    data["Frequency of Traveling by Air"] = data["Frequency of Traveling by Air"].map({'never':0, 'rarely':1, "frequently":2, "very frequently":3})
    data["Waste Bag Size"] = data["Waste Bag Size"].map({'small':0, 'medium':1, "large":2,  "extra large":3})
    data["Energy efficiency"] = data["Energy efficiency"].map({'No':0, 'Sometimes':1, "Yes":2})
    return data
def hesapla(model,ss, sample_df):
    copy_df = sample_df.copy()
    travels = copy_df[["Frequency of Traveling by Air",
                         "Vehicle Monthly Distance Km",
                         'Transport_private',
                          'Transport_public',
                          'Transport_walk/bicycle',
                          'Vehicle Type_None',
                          'Vehicle Type_diesel',
                          'Vehicle Type_electric',
                          'Vehicle Type_hybrid',
                          'Vehicle Type_lpg',
                          'Vehicle Type_petrol']]
    copy_df[list(set(copy_df.columns) - set(travels.columns))] = 0
    travel = np.exp(model.predict(ss.transform(copy_df)))

    copy_df = sample_df.copy()
    energys = copy_df[[ 'Heating Energy Source_coal','How Often Shower', 'How Long TV PC Daily Hour',
                         'Heating Energy Source_electricity','How Long Internet Daily Hour',
                         'Heating Energy Source_natural gas',
                         'Cooking_with_stove',
                          'Cooking_with_oven',
                          'Cooking_with_microwave',
                          'Cooking_with_grill',
                          'Cooking_with_airfryer',
                         'Heating Energy Source_wood','Energy efficiency']]
    copy_df[list(set(copy_df.columns) - set(energys.columns))] = 0
    energy = np.exp(model.predict(ss.transform(copy_df)))

    copy_df = sample_df.copy()
    wastes = copy_df[[  'Do You Recyle_Paper','How Many New Clothes Monthly',
                         'Waste Bag Size',
                         'Waste Bag Weekly Count',
                         'Do You Recyle_Plastic',
                         'Do You Recyle_Glass',
                         'Do You Recyle_Metal',
                         'Social Activity',]]
    copy_df[list(set(copy_df.columns) - set(wastes.columns))] = 0
    waste = np.exp(model.predict(ss.transform(copy_df)))

    copy_df = sample_df.copy()
    diets = copy_df[[ 'Diet_omnivore',
                     'Diet_pescatarian',
                     'Diet_vegan',
                     'Diet_vegetarian', 'Monthly Grocery Bill','Transport_private',
                     'Transport_public',
                     'Transport_walk/bicycle',
                      'Heating Energy Source_coal',
                      'Heating Energy Source_electricity',
                      'Heating Energy Source_natural gas',
                      'Heating Energy Source_wood',
                      ]]
    copy_df[list(set(copy_df.columns) - set(diets.columns))] = 0
    diet = np.exp(model.predict(ss.transform(copy_df)))
    hesap = {"Travel": travel[0], "Energy": energy[0], "Waste": waste[0], "Diet": diet[0]}

    return hesap


# Colours for the four result categories (same order as the dict returned by hesapla)
CHART_COLORS = ["#1b7f79", "#2fb5a3", "#8fd1b1", "#d4ebbf"]       # Travel, Energy, Waste, Diet
CHART_TEXT_COLORS = ["#ffffff", "#0b3b35", "#14412f", "#2b4a1f"]   # readable text on each colour
FOOT_COLOR = (47, 107, 58, 255)


def chart(model, scaler, sample_df, prediction):
    """Return a clean, transparent donut chart (PNG bytes) of the emission breakdown.

    The headline number and title are rendered as HTML in app.py, so this image only
    contains the chart itself. That keeps it sharp, centred and responsive.
    """
    p = hesapla(model, scaler, sample_df)
    labels = list(p.keys())
    values = np.array([float(v) for v in p.values()])
    shares = values / values.sum() * 100

    display_font = font_manager.FontProperties(
        fname=os.path.join(BASE_DIR, "style", "ArchivoBlack-Regular.ttf")
    )

    fig, ax = plt.subplots(figsize=(6, 6.4), dpi=160)
    wedges, _ = ax.pie(
        values,
        colors=CHART_COLORS,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=3),
    )
    ax.set_aspect("equal")

    # percentage labels centred on each ring segment
    for wedge, share, text_color in zip(wedges, shares, CHART_TEXT_COLORS):
        angle = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        radius = 1 - 0.2
        ax.text(radius * np.cos(angle), radius * np.sin(angle), f"{share:.0f}%",
                ha="center", va="center", fontsize=17, color=text_color,
                fontproperties=display_font)

    # footprint icon in the middle of the donut, tinted to match the theme
    foot = Image.open(os.path.join(BASE_DIR, "media", "ayak.png")).convert("RGBA")
    tinted = Image.new("RGBA", foot.size, FOOT_COLOR)
    tinted.putalpha(foot.getchannel("A"))
    ax.add_artist(AnnotationBbox(OffsetImage(np.asarray(tinted), zoom=0.27), (0, 0), frameon=False))

    legend = ax.legend(
        wedges, labels,
        loc="upper center", bbox_to_anchor=(0.5, -0.02),
        ncol=4, frameon=False, fontsize=13, handlelength=1.0, handleheight=1.0,
        columnspacing=1.4, handletextpad=0.5,
    )
    for text in legend.get_texts():
        text.set_color("#1f3a2a")
        text.set_fontweight("bold")

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)  # free memory - otherwise every click leaves an open figure
    buffer.seek(0)
    return buffer
