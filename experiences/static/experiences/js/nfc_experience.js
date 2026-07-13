(function () {
  "use strict";

  var shareButton = document.querySelector("[data-share]");
  var feedback = document.querySelector("[data-feedback]");
  var greeting = document.querySelector("[data-greeting]");
  var pageUrl = window.location.origin + window.location.pathname;

  if (greeting) {
    var hour = new Date().getHours();
    greeting.textContent = hour < 12 ? "Buenos días" : hour < 20 ? "Buenas tardes" : "Buenas noches";
  }

  function showFeedback(message) {
    if (!feedback) return;
    feedback.textContent = message;
    window.setTimeout(function () { feedback.textContent = ""; }, 2600);
  }

  function copyText(text, message) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { showFeedback(message); });
    }
    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
    showFeedback(message);
    return Promise.resolve();
  }

  if (shareButton) {
    shareButton.addEventListener("click", function () {
      var data = { title: shareButton.dataset.title, text: shareButton.dataset.text, url: pageUrl };
      if (navigator.share) {
        navigator.share(data).catch(function (error) {
          if (error.name !== "AbortError") showFeedback("No se pudo abrir el menú para compartir.");
        });
      } else {
        copyText(data.text + "\n\n" + pageUrl, "Enlace copiado. Ya puedes compartirlo.");
      }
    });
  }

}());
