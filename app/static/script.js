const API_URL = "";
// Because our page is served from the same origin as the API,
// we can use relative paths: "/login", "/register", "/books"

const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");
const authForm = document.getElementById("auth-form");
const toggleAuth = document.getElementById("toggle-auth");
const authTitle = document.getElementById("auth-title");
const authButton = document.getElementById("auth-button");
const authError = document.getElementById("auth-error");

// Book elements
const bookForm = document.getElementById("book-form");
const bookList = document.getElementById("book-list");
const bookError = document.getElementById("book-error");
const nameFilter = document.getElementById("name-filter");
const authorFilter = document.getElementById("author-filter");
const publisherFilter = document.getElementById("publisher-filter");
const applyBookFiltersBtn = document.getElementById("apply-book-filters");
const clearBookFiltersBtn = document.getElementById("clear-book-filters");

// Task elements
const taskForm = document.getElementById("task-form");
const taskList = document.getElementById("task-list");
const taskError = document.getElementById("task-error");
const taskTitleFilter = document.getElementById("task-title-filter");
const taskStatusFilter = document.getElementById("task-status-filter");
const applyTaskFiltersBtn = document.getElementById("apply-task-filters");
const clearTaskFiltersBtn = document.getElementById("clear-task-filters");

const logoutBtn = document.getElementById("logout");

let mode = "login"; // or "register"

// Helpers
function showAuth(show) {
  authSection.classList.toggle("hidden", !show);
  appSection.classList.toggle("hidden", show);
}

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

// Generic API caller for JSON endpoints
async function api(path, opts = {}) {
  const headers = {};
  if (path !== "/login") headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let body = opts.body;
  if (body && headers["Content-Type"] === "application/json") {
    body = JSON.stringify(body);
  }

  const res = await fetch(path, { ...opts, headers, body });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.status === 204 ? null : res.json();
}

//Auth 
authForm.addEventListener("submit", async e => {
  e.preventDefault();
  authError.textContent = "";

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    if (mode === "login") {
      // login expects form‑urlencoded
      const form = new URLSearchParams({ username, password });
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      const { access_token } = await res.json();
      setToken(access_token);
      showAuth(false);
      loadBooks();
      loadTasks();
    } else {
      // register expects JSON
      await api("/register", {
        method: "POST",
        body: { username, password },
      });
      mode = "login";
      authTitle.textContent = "Login";
      authButton.textContent = "Login";
      authError.textContent = "Registered! Please log in.";
    }
  } catch (err) {
    authError.textContent = err.message;
  }
});

toggleAuth.addEventListener("click", e => {
  e.preventDefault();
  mode = mode === "login" ? "register" : "login";
  authTitle.textContent = mode === "login" ? "Login" : "Register";
  authButton.textContent = mode === "login" ? "Login" : "Sign Up";
  toggleAuth.querySelector("a").textContent =
    mode === "login" ? "Register" : "Login";
});

//  Books 
function getBookFilters() {
  return {
    name: nameFilter.value,
    author: authorFilter.value,
    publisher: publisherFilter.value
  };
}

async function loadBooks(filters = {}) {
  bookError.textContent = "";
  bookList.innerHTML = "";
  try {
    let url = "/books/";
    const params = new URLSearchParams();
    if (filters.name) params.append("name", filters.name);
    if (filters.author) params.append("author", filters.author);
    if (filters.publisher) params.append("publisher", filters.publisher);
    if (params.toString()) url += "?" + params.toString();

    const books = await api(url);
    for (const b of books) {
      const li = document.createElement("li");
      li.innerHTML = `
        <div>
          <strong>${b.book_name}</strong> by ${b.author}
          <br>
          <small>Publisher: ${b.publisher} | Pages: ${b.pages}</small>
          ${b.description ? `<p>${b.description}</p>` : ''}
        </div>
      `;
      const btn = document.createElement("button");
      btn.textContent = "Delete";
      btn.onclick = async () => {
        try {
          await api(`/books/${b.id}`, { method: "DELETE" });
          loadBooks(getBookFilters());
        } catch (e) {
          bookError.textContent = e.message;
        }
      };
      li.appendChild(btn);
      bookList.appendChild(li);
    }
  } catch (err) {
    bookError.textContent = err.message;
  }
}

bookForm.addEventListener("submit", async e => {
  e.preventDefault();
  bookError.textContent = "";

  const book = {
    book_name: document.getElementById("book_name").value,
    author: document.getElementById("author").value,
    publisher: document.getElementById("publisher").value,
    pages: +document.getElementById("pages").value,
    description: document.getElementById("description").value,
  };

  try {
    await api("/books/", { method: "POST", body: book });
    bookForm.reset();
    loadBooks(getBookFilters());
  } catch (err) {
    bookError.textContent = err.message;
  }
});

// Book filter handlers
applyBookFiltersBtn.addEventListener("click", () => {
  loadBooks(getBookFilters());
});

clearBookFiltersBtn.addEventListener("click", () => {
  nameFilter.value = "";
  authorFilter.value = "";
  publisherFilter.value = "";
  loadBooks();
});

// Tasks
function getTaskFilters() {
  const filters = {
    title: taskTitleFilter.value
  };
  
  // Only add completed filter if a specific status is selected
  const status = taskStatusFilter.value;
  if (status === 'true' || status === 'false') {
    filters.completed = status === 'true';
  }
  
  return filters;
}

async function loadTasks(filters = {}) {
  taskError.textContent = "";
  taskList.innerHTML = "";
  try {
    let url = "/tasks/";
    const params = new URLSearchParams();
    if (filters.title) params.append("title", filters.title);
    if (filters.completed !== undefined) params.append("completed", filters.completed);
    if (params.toString()) url += "?" + params.toString();

    const tasks = await api(url);
    for (const t of tasks) {
      const li = document.createElement("li");
      li.className = t.completed ? "task-completed" : "";
      
      li.innerHTML = `
        <h3>${t.title}</h3>
        ${t.description ? `<p>${t.description}</p>` : ''}
        <div class="task-actions">
          <button class="complete-task" data-id="${t.id}">
            ${t.completed ? "Completed" : "Complete"}
          </button>
          <button class="delete-task" data-id="${t.id}">Delete</button>
        </div>
      `;

      const completeBtn = li.querySelector(".complete-task");
      completeBtn.onclick = async () => {
        try {
          await api(`/tasks/${t.id}/complete`, { method: "POST" });
          loadTasks(getTaskFilters());
        } catch (e) {
          taskError.textContent = e.message;
        }
      };

      const deleteBtn = li.querySelector(".delete-task");
      deleteBtn.onclick = async () => {
        try {
          await api(`/tasks/${t.id}`, { method: "DELETE" });
          loadTasks(getTaskFilters());
        } catch (e) {
          taskError.textContent = e.message;
        }
      };

      taskList.appendChild(li);
    }
  } catch (err) {
    taskError.textContent = err.message;
  }
}

taskForm.addEventListener("submit", async e => {
  e.preventDefault();
  taskError.textContent = "";

  const task = {
    title: document.getElementById("task-title").value,
    description: document.getElementById("task-description").value,
    completed: false
  };

  try {
    await api("/tasks/", { method: "POST", body: task });
    taskForm.reset();
    loadTasks(getTaskFilters());
  } catch (err) {
    taskError.textContent = err.message;
  }
});

// Task filter handlers
applyTaskFiltersBtn.addEventListener("click", () => {
  loadTasks(getTaskFilters());
});

clearTaskFiltersBtn.addEventListener("click", () => {
  taskTitleFilter.value = "";
  taskStatusFilter.value = "";
  loadTasks();
});

// Logout 
logoutBtn.addEventListener("click", () => {
  clearToken();
  showAuth(true);
});

// Init
if (getToken()) {
  showAuth(false);
  loadBooks();
  loadTasks();
} else {
  showAuth(true);
}
