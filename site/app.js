const copyButton = document.querySelector("#copy-email");
const feedback = document.querySelector("#copy-feedback");
const manualCopy = document.querySelector("#manual-copy");
const emailAddress = "stackctrlz@gmail.com";
let feedbackTimer;

copyButton.addEventListener("click", async () => {
  window.clearTimeout(feedbackTimer);

  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error("Clipboard API is unavailable");
    }

    await navigator.clipboard.writeText(emailAddress);
    feedback.textContent = "Copiado: stackctrlz@gmail.com";
    manualCopy.hidden = true;
    copyButton.dataset.copied = "true";
  } catch {
    feedback.textContent = "No se pudo copiar la dirección.";
    manualCopy.hidden = false;
    delete copyButton.dataset.copied;
  }

  feedbackTimer = window.setTimeout(() => {
    feedback.textContent = "";
    delete copyButton.dataset.copied;
  }, 2800);
});
