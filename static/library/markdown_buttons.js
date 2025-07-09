document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.querySelector("textarea");
    if (!textarea) return;
  
    const buttons = [
      { label: "H1", insert: "# " },
      { label: "H2", insert: "## " },
      { label: "Bold", insert: "**bold**" },
      { label: "Italic", insert: "*italic*" },
      { label: "Code", insert: "`code`" },
      { label: "Quote", insert: "> quote\n" },
      { label: "List", insert: "- item\n" },
      { label: "Link", insert: "[text](url)" },
      { label: "Image", insert: "![alt](url)" },
    ];
  
    const toolbar = document.createElement("div");
    toolbar.style.marginBottom = "6px";
    toolbar.style.display = "flex";
    toolbar.style.flexWrap = "wrap";
    toolbar.style.gap = "6px";
  
    buttons.forEach((btn) => {
      const b = document.createElement("button");
      b.type = "button";
      b.innerText = btn.label;
      b.className = "button markdownx-shortcut-btn";
      b.style.padding = "4px 8px";
      b.style.border = "1px solid #ccc";
      b.style.borderRadius = "4px";
      b.style.background = "#333";          // 深灰背景
      b.style.color = "#fff";               // 白色文字
      b.style.cursor = "pointer";
      b.onmouseover = () => b.style.background = "#444";
      b.onmouseout = () => b.style.background = "#333";
      b.onclick = () => {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const before = textarea.value.substring(0, start);
        const after = textarea.value.substring(end);
        textarea.value = before + btn.insert + after;
        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd = start + btn.insert.length;
      };
      toolbar.appendChild(b);
    });
  
    textarea.parentNode.insertBefore(toolbar, textarea);
  });