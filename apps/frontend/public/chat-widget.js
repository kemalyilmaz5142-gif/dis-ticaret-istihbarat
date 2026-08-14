(function () {
  var currentScript = document.currentScript;
  var apiUrl = (currentScript && currentScript.getAttribute("data-api-url")) || "http://localhost:8000/api";
  var language = (currentScript && currentScript.getAttribute("data-language")) || "tr";

  var button = document.createElement("button");
  button.textContent = "Chat";
  button.style.position = "fixed";
  button.style.right = "18px";
  button.style.bottom = "18px";
  button.style.zIndex = "9999";
  button.style.border = "0";
  button.style.borderRadius = "8px";
  button.style.background = "#0f766e";
  button.style.color = "#fff";
  button.style.padding = "12px 16px";
  button.style.fontFamily = "Arial, sans-serif";
  button.style.fontWeight = "700";

  var panel = document.createElement("div");
  panel.style.display = "none";
  panel.style.position = "fixed";
  panel.style.right = "18px";
  panel.style.bottom = "70px";
  panel.style.width = "320px";
  panel.style.background = "#fff";
  panel.style.border = "1px solid #d9dee7";
  panel.style.borderRadius = "8px";
  panel.style.boxShadow = "0 12px 30px rgba(0,0,0,.12)";
  panel.style.zIndex = "9999";
  panel.style.padding = "12px";
  panel.style.fontFamily = "Arial, sans-serif";

  panel.innerHTML = [
    '<strong style="display:block;margin-bottom:8px">Export Assistant</strong>',
    '<div id="ti-widget-reply" style="font-size:13px;color:#667085;margin-bottom:8px">Merhaba, nasil yardimci olabilirim?</div>',
    '<input id="ti-widget-email" placeholder="E-posta" style="width:100%;box-sizing:border-box;margin-bottom:6px;padding:8px;border:1px solid #d9dee7;border-radius:6px" />',
    '<input id="ti-widget-phone" placeholder="Telefon" style="width:100%;box-sizing:border-box;margin-bottom:6px;padding:8px;border:1px solid #d9dee7;border-radius:6px" />',
    '<textarea id="ti-widget-message" placeholder="Mesajiniz" style="width:100%;box-sizing:border-box;min-height:72px;padding:8px;border:1px solid #d9dee7;border-radius:6px"></textarea>',
    '<button id="ti-widget-send" style="margin-top:8px;width:100%;border:0;border-radius:6px;background:#0f766e;color:#fff;padding:10px;font-weight:700">Gonder</button>'
  ].join("");

  button.onclick = function () {
    panel.style.display = panel.style.display === "none" ? "block" : "none";
  };

  panel.addEventListener("click", function (event) {
    if (event.target && event.target.id === "ti-widget-send") {
      var payload = {
        message: document.getElementById("ti-widget-message").value,
        visitor_email: document.getElementById("ti-widget-email").value || null,
        visitor_phone: document.getElementById("ti-widget-phone").value || null,
        page_url: window.location.href,
        language: language
      };
      fetch(apiUrl + "/widget/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          document.getElementById("ti-widget-reply").textContent = data.reply + " " + data.next_question;
        })
        .catch(function () {
          document.getElementById("ti-widget-reply").textContent = "Mesaj alindi, ekip en kisa surede donecek.";
        });
    }
  });

  document.body.appendChild(button);
  document.body.appendChild(panel);
})();
