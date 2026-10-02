(function () {
    var doc = window.parent.document;

    /* ---------- "Did you know" box ---------- */
    var facts = [
        "Each year, human activities release over 40 billion tonnes of CO₂ into the atmosphere.",
        "Producing one kilogram of beef is associated with roughly 26 kg of CO₂e emissions.",
        "Transport accounts for nearly a quarter of global energy-related CO₂ emissions.",
        "Deforestation contributes to about 10% of global carbon emissions by releasing the carbon stored in trees.",
        "Driving an electric vehicle can cut an individual's driving emissions by around half compared with a petrol car, depending on how the electricity is generated.",
        "Streaming an hour of video is estimated to emit only tens of grams of CO₂e, far less than most daily travel.",
        "Globally, buildings are responsible for roughly 36% of total energy use and 39% of energy-related CO₂ emissions.",
        "The fashion industry is estimated to emit around 3.3 billion tonnes of CO₂e every year.",
        "The global average temperature has risen by about 1.2 °C compared with pre-industrial levels.",
        "Rainforests such as the Amazon store huge amounts of carbon, which is released when they are cleared or burned.",
        "In 2019, renewable energy supplied about 26% of the world's electricity.",
        "The world consumes over 90 million barrels of crude oil every day.",
        "Approximately 1.3 billion tonnes of food are wasted globally each year, leading to significant emissions.",
        "Aviation is responsible for roughly 2% of global CO₂ emissions.",
        "In 2020, global CO₂ emissions fell by around 5.8% because of the COVID-19 pandemic.",
        "Producing one tonne of cement releases about 0.6 to 0.9 tonnes of CO₂.",
        "Over 1.5 billion new smartphones are manufactured each year, adding to e-waste and emissions.",
        "Burning fossil fuels for energy accounts for over 70% of global greenhouse gas emissions.",
        "Around 7 million hectares of forest are lost to deforestation every year.",
        "The Paris Agreement aims to limit global warming to well below 2 °C above pre-industrial levels.",
        "Roughly a quarter of the world's population still cooks with biomass such as wood or charcoal.",
        "The ocean absorbs about 30% of the CO₂ released into the atmosphere, which leads to ocean acidification.",
        "Over 8 million tonnes of plastic enter the oceans every year.",
        "The construction and buildings sector is responsible for nearly 40% of global energy-related CO₂ emissions.",
        "The average American generates over 16 tonnes of CO₂ emissions per year."
    ];

    /* The click handler is injected into the MAIN page (not this helper iframe),
       because Streamlit replaces the iframe on every rerun and a handler that lives
       inside it stops working. */
    if (!doc.getElementById('dyk-handler')) {
        var code = 'window.__dykFacts = ' + JSON.stringify(facts) + ';' +
            'document.addEventListener("click", function (e) {' +
            '  var popup = document.getElementById("popup");' +
            '  var btn = document.getElementById("dyk-btn");' +
            '  if (!popup || !btn) { return; }' +
            '  if (e.target.closest("#dyk-btn")) {' +
            '    var t = document.getElementById("popupText");' +
            '    if (t) { t.textContent = window.__dykFacts[Math.floor(Math.random() * window.__dykFacts.length)]; }' +
            '    popup.style.display = "block"; btn.style.display = "none";' +
            '  } else if (e.target.closest("#popup")) {' +
            '    popup.style.display = "none"; btn.style.display = "inline-flex";' +
            '  }' +
            '});';
        var tag = doc.createElement('script');
        tag.id = 'dyk-handler';
        tag.textContent = code;
        doc.head.appendChild(tag);
    }

    /* ---------- button icons (matched by label, not by fragile DOM paths) ---------- */
    var iconRules = [
        { re: /see my footprint/i, cls: 'btn-icon-foot' },
        { re: /calculate again/i,  cls: 'btn-icon-calc' },
        { re: /calculate your carbon footprint/i, cls: 'btn-icon-calc' }
    ];

    Array.from(doc.querySelectorAll('div[data-testid="stButton"] > button')).forEach(function (button) {
        iconRules.forEach(function (rule) {
            if (rule.re.test(button.textContent)) { button.classList.add(rule.cls); }
        });
    });
})();
