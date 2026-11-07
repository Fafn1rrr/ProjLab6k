// Poga «Aprēķināt plānu»: nosūta pieprasījumu serverim un parāda rezultātu vai kļūdu.
document.getElementById("optimize-btn").addEventListener("click", async () => {
  const button = document.getElementById("optimize-btn");
  const result = document.getElementById("result");
  button.disabled = true;
  button.textContent = "Aprēķina…";

  try {
    const response = await fetch("/api/optimize", { method: "POST" });
    const data = await response.json();
    if (response.ok) {
      window.location.href = `/plans/${data.plan_id}`; // atveram saglabāto plānu
      return;
    }
    result.className = "alert alert-danger mt-4";
    result.textContent = data.error; // textContent — teksts netiek interpretēts kā HTML
  } catch (err) {
    result.className = "alert alert-danger mt-4";
    result.textContent = "Servera kļūda. Paskatieties terminālī, kur darbojas lietotne.";
  }

  button.disabled = false;
  button.textContent = "Aprēķināt plānu";
});
