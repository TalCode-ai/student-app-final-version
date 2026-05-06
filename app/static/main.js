"use strict";

{
  // ── DOM References ────────────────────────────────────────────
  const tbody       = document.getElementById("tbody");
  const idBox       = document.getElementById("idBox");
  const nameBox     = document.getElementById("nameBox");
  const ageBox      = document.getElementById("ageBox");
  const btAdd       = document.getElementById("btAdd");
  const btUpdate    = document.getElementById("btUpdate");
  const btDelete    = document.getElementById("btDelete");
  const themeSelect = document.getElementById("themeSelect");

  // ── Theme Switcher ────────────────────────────────────────────
  const THEME_KEY = "students-app-theme";
  const themes = [
    "theme-dark",
    "theme-light",
    "theme-ocean",
    "theme-forest",
    "theme-sunset",
    "theme-midnight",
  ];

  function applyTheme(theme) {
    document.body.classList.remove(...themes);
    document.body.classList.add(theme);
    localStorage.setItem(THEME_KEY, theme);
  }

  const savedTheme = localStorage.getItem(THEME_KEY) || "theme-dark";
  themeSelect.value = savedTheme;
  applyTheme(savedTheme);

  themeSelect.addEventListener("change", () => {
    applyTheme(themeSelect.value);
  });

  // ── Add Student ───────────────────────────────────────────────
  btAdd.addEventListener("click", async () => {
    const name = nameBox.value.trim();
    const age  = ageBox.value;

    if (!name || !age) {
      alert("⚠️ Please enter both a Name and Age before adding a student.");
      return;
    }

    // const confirmed = confirm(
    //   `➕ Add new student?\n\n` +
    //   `  Name : ${name}\n` +
    //   `  Age  : ${age}\n\n` +
    //   `Click OK to confirm.`
    // );
    // if (!confirmed) return;

    try {
      const response = await axios.post("/students", { name, age });
      console.log("Student added:", response.data);
      clearForm();
    } catch (error) {
      if (error.response?.status === 400) {
        alert("❌ Validation Error: " + (error.response.data.message || "No message."));
      } else {
        alert("❌ Connection failed!");
      }
    }

    await getAll();
  });

  // ── Update Student ────────────────────────────────────────────
  btUpdate.addEventListener("click", async () => {
    const id   = +idBox.value;
    const name = nameBox.value.trim();
    const age  = +ageBox.value;

    if (!id || !name || !age) {
      alert("⚠️ Please fill in the ID, Name and Age fields before updating.");
      return;
    }

    const confirmed = confirm(
      `✏️ Update student #${id}?\n\n` +
      `  New Name : ${name}\n` +
      `  New Age  : ${age}\n\n` +
      `Click OK to confirm.`
    );
    if (!confirmed) return;

    try {
      await axios.put("/students", { id, name, age });
      clearForm();
      await getAll();
    } catch (error) {
      alert("❌ " + (error.response?.data?.message ?? "Update failed."));
    }
  });

  // ── Delete Student (by input ID) ──────────────────────────────
  btDelete.addEventListener("click", () => {
    const id = idBox.value;
    if (!id) {
      alert("⚠️ Please enter the ID of the student you want to delete.");
      return;
    }
    deleteStudent(id);
  });

  async function deleteStudent(id) {
    const confirmed = confirm(
      `🗑️ Delete student #${id}?\n\n` +
      `This action cannot be undone.\n\n` +
      `Click OK to confirm.`
    );
    if (!confirmed) return;

    try {
      await axios.delete(`/students/${id}`);
      clearForm();
      await getAll();
    } catch (error) {
      alert("❌ " + (error.response?.data?.message ?? "Delete failed."));
    }
  }

  // ── Fill Form from Table Row ──────────────────────────────────
  function fillForm(id, name, age) {
    idBox.value   = id;
    nameBox.value = name;
    ageBox.value  = age;

    // Smooth scroll to the form on mobile
    document.querySelector(".form-card").scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

    // Briefly highlight the form to draw attention
    const card = document.querySelector(".form-card");
    card.classList.add("form-highlight");
    setTimeout(() => card.classList.remove("form-highlight"), 1200);
  }

  // ── Clear Form ────────────────────────────────────────────────
  function clearForm() {
    idBox.value   = "";
    nameBox.value = "";
    ageBox.value  = "";
  }

  // ── Fetch & Render All Students ───────────────────────────────
  async function getAll() {
    try {
      const response = await axios.get("/students");
      const students = response.data;

      tbody.innerHTML = students
        .map(
          (s) => `
          <tr>
            <td>${s.id}</td>
            <td>${s.name}</td>
            <td>${s.age}</td>
            <td>
              <button
                class="edit-btn"
                data-id="${s.id}"
                data-name="${s.name}"
                data-age="${s.age}"
                title="Load into form for editing">
                ✏️ Edit
              </button>
            </td>
            <td>
              <button
                class="delete-btn"
                data-id="${s.id}"
                title="Delete this student">
                ✕ Remove
              </button>
            </td>
          </tr>`
        )
        .join("");

      // Edit buttons — load row data into the form
      tbody.querySelectorAll(".edit-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          fillForm(
            btn.getAttribute("data-id"),
            btn.getAttribute("data-name"),
            btn.getAttribute("data-age")
          );
        });
      });

      // Delete buttons — delete directly from the table
      tbody.querySelectorAll(".delete-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          deleteStudent(btn.getAttribute("data-id"));
        });
      });

    } catch (error) {
      console.error("Failed to load students:", error);
    }
  }

  // ── Init ──────────────────────────────────────────────────────
  window.addEventListener("load", getAll);
}