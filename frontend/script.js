// =====================================
// SKILLBRIDGE FRONTEND CONFIGURATION
// =====================================

const API_URL = "http://127.0.0.1:8000";


// =====================================
// GET HTML ELEMENTS
// =====================================

const authModal = document.getElementById("authModal");

const closeAuth = document.getElementById("closeAuth");

const loginForm = document.getElementById("loginForm");

const signupForm = document.getElementById("signupForm");

const authTitle = document.getElementById("authTitle");

const authSubtitle = document.getElementById("authSubtitle");

const authMessage = document.getElementById("authMessage");


// =====================================
// OPEN AUTHENTICATION POPUP
// =====================================

function openAuth(type) {

    authModal.classList.add("active");

    authMessage.textContent = "";
    authMessage.className = "auth-message";

    if (type === "signup") {
        showSignupForm();
    } else {
        showLoginForm();
    }
}


// =====================================
// CLOSE AUTHENTICATION POPUP
// =====================================

function closeAuthModal() {
    authModal.classList.remove("active");
}

closeAuth.addEventListener("click", closeAuthModal);

authModal.addEventListener("click", function (event) {

    if (event.target === authModal) {
        closeAuthModal();
    }

});


// =====================================
// SWITCH TO SIGNUP FORM
// =====================================

function showSignupForm() {

    loginForm.style.display = "none";
    signupForm.style.display = "flex";

    authTitle.textContent = "Create Your Account";

    authSubtitle.textContent =
        "Start building your future with SkillBridge.";

    authMessage.textContent = "";
}


// =====================================
// SWITCH TO LOGIN FORM
// =====================================

function showLoginForm() {

    signupForm.style.display = "none";
    loginForm.style.display = "flex";

    authTitle.textContent = "Welcome Back!";

    authSubtitle.textContent =
        "Log in to continue your career journey.";

    authMessage.textContent = "";
}


// =====================================
// SWITCH BUTTONS
// =====================================

document.getElementById("showLogin").addEventListener(
    "click",
    function (event) {

        event.preventDefault();
        showLoginForm();

    }
);


document.getElementById("showSignup").addEventListener(
    "click",
    function (event) {

        event.preventDefault();
        showSignupForm();

    }
);


// =====================================
// NAVBAR BUTTONS
// =====================================

document.querySelector(".login-button").addEventListener(
    "click",
    function (event) {

        event.preventDefault();
        openAuth("login");

    }
);


document.querySelector(".signup-button").addEventListener(
    "click",
    function (event) {

        event.preventDefault();
        openAuth("signup");

    }
);


// GET STARTED BUTTON

document.querySelector(".primary-button").addEventListener(
    "click",
    function (event) {

        event.preventDefault();
        openAuth("signup");

    }
);


// =====================================
// STUDENT REGISTRATION
// POST /students
// =====================================

signupForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const name = document.getElementById("signupName").value.trim();

    const email = document.getElementById("signupEmail").value.trim();

    const password = document.getElementById("signupPassword").value;

    const submitButton = signupForm.querySelector(".auth-submit");

    submitButton.disabled = true;
    submitButton.textContent = "Creating Account...";

    try {

        const response = await fetch(`${API_URL}/students`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Registration failed.");
        }

        authMessage.textContent =
            "Account created successfully! Please log in.";

        authMessage.className = "auth-message success";

        signupForm.reset();

        setTimeout(function () {
            showLoginForm();

            document.getElementById("loginEmail").value = email;

        }, 1500);

    }

    catch (error) {

        authMessage.textContent = error.message;

        authMessage.className = "auth-message error";

    }

    finally {

        submitButton.disabled = false;
        submitButton.textContent = "Create Account";

    }

});


// =====================================
// STUDENT LOGIN
// POST /login
// =====================================

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();

    const password = document.getElementById("loginPassword").value;

    const submitButton = loginForm.querySelector(".auth-submit");

    submitButton.disabled = true;
    submitButton.textContent = "Logging in...";

    try {

        const response = await fetch(`${API_URL}/login`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed.");
        }
        console.log("LOGIN SUCCESSFUL");
        console.log("Redirecting to:", window.location.origin + "/dashboard.html");
        // Store authentication information

        localStorage.setItem("access_token", data.access_token);

        localStorage.setItem(
            "student",
            JSON.stringify(data.student)
        );

        authMessage.textContent = "Login successful!";

        authMessage.className = "auth-message success";

setTimeout(function () {
    window.location.href = "/frontend/dashboard.html";
}, 1000);

 }

    catch (error) {

        authMessage.textContent = error.message;

        authMessage.className = "auth-message error";

    }

    finally {

        submitButton.disabled = false;
        submitButton.textContent = "Log In";

    }
});
// =====================================
// LOAD JOB ROLES FROM FASTAPI
// GET /roles
// =====================================
// =====================================
// LOAD JOB ROLES FROM FASTAPI
// GET /roles
// =====================================

const careerSection = document.getElementById("careerSection");
const careerSelect = document.getElementById("careerSelect");
const careerSearch = document.getElementById("careerSearch");
const careerMessage = document.getElementById("careerMessage");

let allCareerRoles = [];

async function loadCareerRoles() {

    try {

        const response = await fetch(`${API_URL}/roles`);

        if (!response.ok) {
            throw new Error("Unable to load job roles.");
        }

        const data = await response.json();

        allCareerRoles = data.roles;

        displayCareerRoles(allCareerRoles);

    }

    catch (error) {

        careerSelect.innerHTML =
            '<option value="">Failed to load job roles</option>';

        careerMessage.textContent = error.message;

    }

}


// =====================================
// DISPLAY JOB ROLES
// =====================================

function displayCareerRoles(roles) {

    careerSelect.innerHTML =
        '<option value="">Choose your target career</option>';

    roles.forEach(function (role) {

        const option = document.createElement("option");

        option.value = role.role_id;

        option.textContent =
            `${role.job_role} (${role.sector})`;

        careerSelect.appendChild(option);

    });

}


// =====================================
// SEARCH JOB ROLES
// =====================================

careerSearch.addEventListener("input", function () {

    const searchText = careerSearch.value.toLowerCase().trim();

    const filteredRoles = allCareerRoles.filter(function (role) {

        return (
            role.job_role.toLowerCase().includes(searchText) ||
            role.sector.toLowerCase().includes(searchText)
        );

    });

    displayCareerRoles(filteredRoles);

});
// =====================================
// DISPLAY JOB ROLES
// =====================================

function displayCareerRoles(roles) {

    careerSelect.innerHTML =
        '<option value="">Choose your target career</option>';

    roles.forEach(function (role) {

        const option = document.createElement("option");

        option.value = role.role_id;

        option.textContent =
            `${role.job_role} (${role.sector})`;

        careerSelect.appendChild(option);

    });

}
// Save the selected job role from the homepage
careerSelect.addEventListener("change", function () {

    const selectedRoleId = careerSelect.value;

    if (selectedRoleId) {
        localStorage.setItem("selected_role_id", selectedRoleId);
    } else {
        localStorage.removeItem("selected_role_id");
    }

});


// =====================================
// SEARCH JOB ROLES
// =====================================

careerSearch.addEventListener("input", function () {

    const searchText = careerSearch.value.toLowerCase().trim();

    const filteredRoles = allCareerRoles.filter(function (role) {

        return (
            role.job_role.toLowerCase().includes(searchText) ||
            role.sector.toLowerCase().includes(searchText)
        );

    });

    displayCareerRoles(filteredRoles);

});
// =====================================
// HANDLE LOGIN AND SELECTED ROLE
// =====================================

const urlParams = new URLSearchParams(window.location.search);

const authAction = urlParams.get("auth");
const requestedRoleId = urlParams.get("role_id");

// Save the selected role if the user came from the careers page
if (requestedRoleId) {
    localStorage.setItem("selected_role_id", requestedRoleId);
}

// Handle direct login
else if (authAction === "login") {
    localStorage.removeItem("selected_role_id");
    localStorage.removeItem("login_source");
}
// Open the login popup
if (authAction === "login") {
    openAuth("login");
}
// =====================================
// SKILL GAP ANALYSIS
// POST /progress/initialize
// =====================================

const continueCareer = document.getElementById("continueCareer");

const studentSkills = document.getElementById("studentSkills");

const skillAnalysisResults = document.getElementById(
    "skillAnalysisResults"
);


continueCareer.addEventListener("click", async function () {

    const roleId = careerSelect.value;

    const skillsInput = studentSkills.value.trim();

    // Check career selection

    if (!roleId) {
        careerMessage.textContent = "Please select a career role.";
        return;
    }

    // Check skills

    if (!skillsInput) {
        careerMessage.textContent = "Please enter your existing skills.";
        return;
    }

    // Convert comma-separated skills into an array

    const skills = skillsInput
        .split(",")
        .map(skill => skill.trim())
        .filter(skill => skill.length > 0);

    const token = localStorage.getItem("access_token");

    if (!token) {
        careerMessage.textContent = "Please log in again.";
        return;
    }

    continueCareer.disabled = true;
    continueCareer.textContent = "Analyzing Your Skills...";

    careerMessage.textContent = "";

    try {

        const response = await fetch(
            `${API_URL}/progress/initialize`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    role_id: Number(roleId),
                    student_skills: skills
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Skill analysis failed.");
        }

        // Display analysis results

        skillAnalysisResults.innerHTML = "";

        const heading = document.createElement("h2");
        heading.textContent = "Your Skill Gap Analysis";

        const role = document.createElement("p");
        role.textContent = `Target Career: ${data.job_role}`;

        const percentage = document.createElement("h3");
        percentage.textContent =
            `Career Match: ${data.initial_match_percentage}%`;

        const matchedHeading = document.createElement("h3");
        matchedHeading.textContent = "Matched Skills";

        const matchedList = document.createElement("ul");

        data.matched_skills.forEach(skill => {
            const item = document.createElement("li");
            item.textContent = "✓ " + skill;
            matchedList.appendChild(item);
        });

        const missingHeading = document.createElement("h3");
        missingHeading.textContent = "Skills to Develop";

        const missingList = document.createElement("ul");

        data.missing_skills.forEach(skill => {
            const item = document.createElement("li");
            item.textContent = "○ " + skill;
            missingList.appendChild(item);
        });

        skillAnalysisResults.append(
            heading,
            role,
            percentage,
            matchedHeading,
            matchedList,
            missingHeading,
            missingList
        );

        careerMessage.textContent =
            "Analysis completed successfully!";

        careerMessage.style.color = "#148451";

        skillAnalysisResults.scrollIntoView({
            behavior: "smooth"
        });

    }

    catch (error) {

        careerMessage.textContent = error.message;
        careerMessage.style.color = "#d93025";

    }

    finally {

        continueCareer.disabled = false;
        continueCareer.textContent = "Analyze My Skills →";

    }

});