window.esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
window.ecStore = {  // the chat, plan and picks, shared by every page
  KEY: "eventcraft_chat_v1",
  load() { try { return JSON.parse(localStorage.getItem(this.KEY) || "null"); } catch (e) { return null; } },
  save(d) { try { localStorage.setItem(this.KEY, JSON.stringify(d)); } catch (e) {} },
};
window.inr = n => "₹" + Number(n).toLocaleString("en-IN");

(function () {
  const links = [
    ["/", "Plan an event", "M4 5h16v11H9l-5 4z"],
    ["/catalog", "Vendor catalog", "M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"],
  ];
  const here = location.pathname.replace(/\/+$/, "") || "/";
  function mount() {
    const a = document.createElement("aside");
    a.className = "rail";
    a.innerHTML = '<a class="brand" href="/"><i aria-hidden="true">E</i>EventCraft</a><nav aria-label="Main">' +
      links.map(([href, label, d]) => `<a href="${href}"${href === here ? ' aria-current="page"' : ""}>` +
        `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${d}"/></svg>${label}</a>`).join("") +
      '</nav><div class="foot">A team of agents plans your event and keeps it inside your budget.</div>';
    document.body.prepend(a);
  }
  if (document.body) mount(); else document.addEventListener("DOMContentLoaded", mount);
})();
