// =====================================
// SKILLBRIDGE DASHBOARD
// =====================================

const API_URL = "http://127.0.0.1:8000";


// =====================================
// CHECK LOGIN
// =====================================

const token = localStorage.getItem("access_token");

const student = JSON.parse(
    localStorage.getItem("student") || "null"
);

if (!token || !student) {
    window.location.href = "index.html";
}


// =====================================
// STUDENT INFORMATION
// =====================================

if (student) {

    const firstLetter = student.name.charAt(0).toUpperCase();

    document.getElementById("welcomeName").textContent =
        student.name.split(" ")[0];

    document.getElementById("sidebarName").textContent =
        student.name;

    document.getElementById("sidebarEmail").textContent =
        student.email;

    document.getElementById("sidebarAvatar").textContent =
        firstLetter;

    document.getElementById("topbarAvatar").textContent =
        firstLetter;
}


// =====================================
// CURRENT DATE
// =====================================

document.getElementById("currentDate").textContent =
    new Date().toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric"
    });


// =====================================
// SIDEBAR NAVIGATION
// =====================================

const navigationItems = document.querySelectorAll(".nav-item");

const pages = document.querySelectorAll(".content-page");

const pageTitle = document.getElementById("pageTitle");

const pageNames = {
    dashboard: "Dashboard",
    analysis: "Skill Analysis",
    resources: "Learning Resources",
    progress: "My Progress",
    internships: "Internships",
    profile: "My Profile",
    settings: "Settings"
};

function showPage(pageName) {

    pages.forEach(page => {
        page.classList.remove("active");
    });

    navigationItems.forEach(item => {
        item.classList.remove("active");
    });

    const selectedPage = document.getElementById(pageName + "Page");

    if (selectedPage) {
        selectedPage.classList.add("active");
    }

    const selectedNav = document.querySelector(
        `[data-page="${pageName}"]`
    );

    if (selectedNav) {
        selectedNav.classList.add("active");
    }

    pageTitle.textContent = pageNames[pageName] || "Dashboard";

    if (pageName === "resources") {
        loadLearningResources();
    }

    if (pageName === "progress") {
        loadMyProgress();
    }
}
// ======================================
// MY PROGRESS
// ======================================

async function loadMyProgress() {

    const progressContent = document.getElementById("progressContent");

    const token = localStorage.getItem("access_token");
    const roleId = localStorage.getItem("selected_role_id");

    if (!roleId) {
        progressContent.innerHTML = `
            <div class="panel">
                <h3>No career selected</h3>
                <p>Complete your Skill Analysis first.</p>
                <button class="primary-button"
                    onclick="showPage('analysis')">
                    Start Skill Analysis →
                </button>
            </div>
        `;
        return;
    }

    progressContent.innerHTML = "<p>Loading your progress...</p>";

    try {

        const response = await fetch(
            `${API_URL}/progress/${roleId}`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {                                                                        
        const errorDetails = await response.text();

        console.error("Progress API Error:", response.status);
        console.error("Error Details:", errorDetails);
        throw new Error(
        `Progress loading failed: ${response.status}`
    );
}

        const data = await response.json();

        displayMyProgress(data);

    } catch (error) {

        console.error(error);

        progressContent.innerHTML = `
            <div class="panel">
                <h3>Unable to load progress</h3>
                <p>Please log in again and try once more.</p>
            </div>
        `;
    }
}


// ======================================
// DISPLAY PROGRESS
// ======================================

function displayMyProgress(data) {

    const progressContent = document.getElementById("progressContent");

    const skills = data.skills || [];

    const completed = skills.filter(skill => skill.progress === 100).length;

    const inProgress = skills.filter(
        skill => skill.progress > 0 && skill.progress < 100
    ).length;

    const notStarted = skills.filter(
        skill => skill.progress === 0
    ).length;

    progressContent.innerHTML = `

        <div class="progress-overview">

            <div class="progress-card">
                <span>Overall Progress</span>
                <h2>${data.overall_progress}%</h2>
            </div>

            <div class="progress-card">
                <span>Total Skills</span>
                <h2>${data.total_skills}</h2>
            </div>

            <div class="progress-card">
                <span>Completed</span>
                <h2>${completed}</h2>
            </div>

            <div class="progress-card">
                <span>In Progress</span>
                <h2>${inProgress}</h2>
            </div>

            <div class="progress-card">
                <span>Not Started</span>
                <h2>${notStarted}</h2>
            </div>

       </div>

        <div class="panel overall-progress-panel">
            <div class="overall-progress-heading">
                <div>
                    <span class="progress-label">YOUR LEARNING JOURNEY</span>
                    <h2>Overall Learning Progress</h2>
                    <p>Keep going! Every completed skill brings you closer to your career goal.</p>
                </div>
                <strong>${Number(data.overall_progress).toFixed(2)}%</strong>
            </div>

            <div class="overall-progress-track">
                <div class="overall-progress-fill"
                     style="width:${Math.min(100, Math.max(0, Number(data.overall_progress) || 0))}%">
                </div>
            </div>
        </div>

        <div class="panel skill-progress-panel">

            <h2>Skill-wise Progress</h2>

            <p>Track your learning journey skill by skill.</p>

            <div id="individualSkillProgress"></div>

        </div>
    `;

    const individualSkillProgress =
        document.getElementById("individualSkillProgress");

    skills.forEach(skill => {

        const percentage = Number(skill.progress) || 0;

        const displayName = skill.skill_name.replace(
            /\b\w/g,
            char => char.toUpperCase()
        );

        const skillItem = document.createElement("div");

        skillItem.className = "individual-skill";

        skillItem.innerHTML = `

            <div class="skill-progress-header">

                <h3>${escapeHTML(displayName)}</h3>

                <span>${percentage}%</span>

            </div>

            <div class="progress-track">

                <div class="progress-fill"
                    style="width: ${percentage}%;">
                </div>

            </div>

            <div class="skill-progress-footer">

                <span>
                    ${
                        percentage === 100
                        ? "Completed"
                        : percentage === 0
                        ? "Not Started"
                        : "In Progress"
                    }
                </span>

                <select class="progress-select"
                    data-skill="${escapeHTML(skill.skill_name)}">

                    <option value="0" ${percentage === 0 ? "selected" : ""}>0%</option>

                    <option value="25" ${percentage === 25 ? "selected" : ""}>25%</option>

                    <option value="50" ${percentage === 50 ? "selected" : ""}>50%</option>

                    <option value="75" ${percentage === 75 ? "selected" : ""}>75%</option>

                    <option value="100" ${percentage === 100 ? "selected" : ""}>100%</option>

                </select>

            </div>

        `;

        individualSkillProgress.appendChild(skillItem);

    });

    // Progress update event

    document.querySelectorAll(".progress-select").forEach(select => {

        select.addEventListener("change", async function () {

            await updateSkillProgress(
                this.dataset.skill,
                Number(this.value)
            );

        });

    });

}


// ======================================
// UPDATE SKILL PROGRESS
// ======================================
async function updateSkillProgress(skillName, percentage) {

    const token = localStorage.getItem("access_token");
    const roleId = localStorage.getItem("selected_role_id");

    try {

        const response = await fetch(
            `${API_URL}/progress/update`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    role_id: Number(roleId),
                    skill_name: skillName,
                    progress_percentage: percentage
                })
            }
        );

        if (!response.ok) {
            throw new Error("Progress update failed.");
        }

        await loadMyProgress();

    } catch (error) {

        console.error(error);

        alert("Unable to update progress. Please try again.");

        await loadMyProgress();
    }
}
// Sidebar clicks

navigationItems.forEach(item => {

    item.addEventListener("click", function (event) {

        event.preventDefault();

        showPage(this.dataset.page);

    });

});


// Dashboard buttons

document.querySelectorAll("[data-go]").forEach(button => {

    button.addEventListener("click", function () {

        showPage(this.dataset.go);

    });

});


// =====================================
// HTML SAFETY
// =====================================

function escapeHTML(value) {

    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);

}


// =====================================
// SKILL ANALYSIS
// =====================================

const analysisContent = document.getElementById("analysisContent");

const savedSkills = localStorage.getItem("entered_student_skills") || "";

// Display Skill Analysis Form
analysisContent.innerHTML = `

    <div class="panel">

        <h2>Discover Your Skill Gaps</h2>

        <p style="color:#858398; margin:12px 0 25px;">
            First select your career category, then choose
            your target job role and enter your existing skills.
        </p>

        <label for="categorySelect">
            <strong>Select Career Category</strong>
        </label>

        <select id="categorySelect"
            style="width:100%; padding:13px; margin-top:10px;
            margin-bottom:25px; border:1px solid #ddd8ec;
            border-radius:9px; background:white;">

            <option value="">Loading categories...</option>

        </select>


        <label for="careerSelect">
            <strong>Select Target Job Role</strong>
        </label>

        <select id="careerSelect"
            disabled
            style="width:100%; padding:13px; margin-top:10px;
            margin-bottom:25px; border:1px solid #ddd8ec;
            border-radius:9px; background:white;">

            <option value="">Select a category first</option>

        </select>


        <label for="studentSkills">
            <strong>Your Existing Skills</strong>
        </label>

        <textarea id="studentSkills"
        placeholder="Example: Python, SQL, Excel, Power BI"
        rows="5"
        style="width:100%; padding:15px; margin-top:10px;
        border:1px solid #ddd8ec; border-radius:9px;
        resize:vertical; font-family:inherit;">${escapeHTML(savedSkills)}
        </textarea>

        <p style="color:#858398; font-size:12px; margin-top:8px;">
            Separate multiple skills using commas.
        </p>

        <button type="button"
    id="analyzeSkillsButton"
    class="primary-button"
    style="margin-top:22px;">
    Analyse My Skills →
</button>
        <p id="analysisMessage"
            style="margin-top:15px; font-size:13px;">
        </p>

    </div>

    <div id="analysisResults"></div>

`;
// =====================================
// LOAD JOB ROLES
// =====================================
// =====================================
// LOAD CATEGORIES AND JOB ROLES
// =====================================
// =====================================
// LOAD CATEGORIES AND JOB ROLES
// =====================================

let allRoles = [];

async function loadJobRoles() {

    const categorySelect = document.getElementById("categorySelect");
    const careerSelect = document.getElementById("careerSelect");
    const message = document.getElementById("analysisMessage");

    try {

        categorySelect.innerHTML =
            `<option value="">Loading categories...</option>`;

        careerSelect.innerHTML =
            `<option value="">Select a category first</option>`;

        careerSelect.disabled = true;

        // Fetch all available job roles
        const response = await fetch(`${API_URL}/roles`);

        if (!response.ok) {
            throw new Error("Failed to fetch job roles.");
        }

        const data = await response.json();

        if (!data.roles || !Array.isArray(data.roles)) {
            throw new Error("Invalid job roles data received.");
        }

        allRoles = data.roles;

        // Extract unique categories
        const categories = [
            ...new Set(
                allRoles
                    .map(role => role.sector)
                    .filter(Boolean)
            )
        ].sort();

        // Populate category dropdown
        categorySelect.innerHTML =
            `<option value="">Choose a career category</option>`;

        categories.forEach(category => {

            const option = document.createElement("option");

            option.value = category;
            option.textContent = category;

            categorySelect.appendChild(option);

        });

        // Restore previously selected role
        const savedRoleId = localStorage.getItem("selected_role_id");

        if (savedRoleId) {

            const savedRole = allRoles.find(
                role => String(role.role_id) === String(savedRoleId)
            );

            if (savedRole) {

                categorySelect.value = savedRole.sector;

                updateCareerOptions(savedRole.sector);

                careerSelect.value = String(savedRoleId);

            }

        }

        console.log("Categories loaded:", categories);
        console.log("Job roles loaded:", allRoles.length);

    } catch (error) {

        console.error("Dropdown loading error:", error);

        categorySelect.innerHTML =
            `<option value="">Unable to load categories</option>`;

        careerSelect.innerHTML =
            `<option value="">Unable to load job roles</option>`;

        if (message) {
            message.textContent =
                "Unable to load categories. Please check the server.";
        }

    }
}


// =====================================
// FILTER JOB ROLES BY CATEGORY
// =====================================

function updateCareerOptions(selectedCategory) {

    const careerSelect = document.getElementById("careerSelect");

    careerSelect.innerHTML =
        `<option value="">Choose your target job role</option>`;

    const filteredRoles = allRoles.filter(
        role => role.sector === selectedCategory
    );

    filteredRoles.forEach(role => {

        const option = document.createElement("option");

        option.value = role.role_id;
        option.textContent = role.job_role;

        careerSelect.appendChild(option);

    });

    careerSelect.disabled = filteredRoles.length === 0;

}


// =====================================
// CATEGORY CHANGE EVENT
// =====================================

document.getElementById("categorySelect")
    .addEventListener("change", function () {

        updateCareerOptions(this.value);

    });
// =====================================
// FILTER ROLES BY CATEGORY
// =====================================

function updateCareerOptions(selectedCategory) {

    const careerSelect =
        document.getElementById("careerSelect");

    careerSelect.innerHTML =
        `<option value="">Choose your target job role</option>`;

    const filteredRoles = allRoles.filter(
        role => role.sector === selectedCategory
    );

    filteredRoles.forEach(role => {

        const option = document.createElement("option");

        option.value = role.role_id;
        option.textContent = role.job_role;

        careerSelect.appendChild(option);

    });

    careerSelect.disabled = filteredRoles.length === 0;

}


// =====================================
// CATEGORY CHANGE EVENT
// =====================================

document.getElementById("categorySelect")
    .addEventListener("change", function () {

        updateCareerOptions(this.value);

    });

// =====================================
// ANALYSE SKILLS
// =====================================

document.getElementById("analyzeSkillsButton").addEventListener(
    "click",
    async function () {

        const roleId = document.getElementById("careerSelect").value;

        const skillsInput = document.getElementById("studentSkills").value;

        const message = document.getElementById("analysisMessage");

        const results = document.getElementById("analysisResults");

        const button = this;
        const token = localStorage.getItem("access_token");
        if (!token) {
        message.textContent = "Your session has expired. Please log in again.";
        return;
        }


        // Validation

        if (!roleId) {

            message.textContent = "Please select a target job role.";

            return;

        }

        if (!skillsInput.trim()) {

            message.textContent = "Please enter at least one existing skill.";

            return;

        }


        const studentSkills = skillsInput
            .split(",")
            .map(skill => skill.trim())
            .filter(skill => skill.length > 0);


        button.disabled = true;

        button.textContent = "Analysing...";

        message.textContent = "Comparing your skills with job requirements...";

        results.innerHTML = "";


        try {

            const response = await fetch(
        `${API_URL}/analyze-skills`,
        {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },

        body: JSON.stringify({
            role_id: Number(roleId),
            student_skills: studentSkills
        })
    }
);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Skill analysis failed."
                );
            }


            // Save selected career
            localStorage.setItem(
                "selected_role_id",
                String(roleId)
            );

            // Display results
            displayAnalysisResults(data);
            message.textContent =
                "Your skill analysis is complete!";
        }

        catch (error) {
            message.textContent = error.message;
            console.error(error);
        }

        finally {
            button.disabled = false;
            button.textContent = "Analyse My Skills →";
        }

    }
);


// =====================================
// DISPLAY ANALYSIS RESULTS
// =====================================

function displayAnalysisResults(data) {

    const results = document.getElementById("analysisResults");

    const matchedSkills = data.matched_skills || [];

    const missingSkills = data.missing_skills || [];

    // Save analysis results for other dashboard pages
localStorage.setItem(
    "missing_skills",
    JSON.stringify(missingSkills)
);

localStorage.setItem(
    "matched_skills",
    JSON.stringify(matchedSkills)
);

// Save skills entered by the student
const enteredSkills = document.getElementById("studentSkills")
    .value
    .split(",")
    .map(skill => skill.trim())
    .filter(Boolean);

localStorage.setItem(
    "entered_student_skills",
    enteredSkills.join(", ")
);

localStorage.setItem(
    "recently_updated_skills",
    JSON.stringify(enteredSkills)
);

// Save total required skills
localStorage.setItem(
    "total_required_skills",
    data.total_required_skills || (matchedSkills.length + missingSkills.length)
);
    const percentage = Number(data.match_percentage || 0);

    results.innerHTML = `
        <div class="panel">

            <p style="
                color:#858398;
                font-size:12px;
                font-weight:600;
            ">
                YOUR CAREER MATCH
            </p>

            <h1 style="
                color:#6941c6;
                font-size:42px;
                margin:10px 0;
            ">
                ${percentage.toFixed(2)}%
            </h1>

            <div style="
                background:#eee8ff;
                height:10px;
                border-radius:20px;
                overflow:hidden;
            ">

                <div style="
                    width:${Math.min(100, Math.max(0, percentage))}%;
                    height:100%;
                    background:#6941c6;
                    border-radius:20px;
                "></div>

            </div>


            <div style="
                display:grid;
                grid-template-columns:repeat(2,minmax(0,1fr));
                gap:20px;
                margin-top:30px;
            ">


                <div>

                    <h3 style="color:#269b67;">
                        ✓ Matched Skills (${matchedSkills.length})
                    </h3>

                    <div style="margin-top:15px;">

                        ${
                            matchedSkills.length
                            ? matchedSkills.map(skill => `
                                <p style="
                                    background:#e9f8ef;
                                    color:#267d53;
                                    padding:10px;
                                    border-radius:7px;
                                    margin-bottom:8px;
                                    font-size:13px;
                                ">
                                    ✓ ${escapeHTML(skill)}
                                </p>
                            `).join("")
                            : "<p>No matched skills found.</p>"
                        }

                    </div>

                </div>


                <div>

                    <h3 style="color:#d17c39;">
                        + Skills to Learn (${missingSkills.length})
                    </h3>

                    <div style="margin-top:15px;">

                        ${
                            missingSkills.length
                            ? missingSkills.map(skill => `
                                <p style="
                                    background:#fff3e8;
                                    color:#a9642e;
                                    padding:10px;
                                    border-radius:7px;
                                    margin-bottom:8px;
                                    font-size:13px;
                                ">
                                    + ${escapeHTML(skill)}
                                </p>
                            `).join("")
                            : "<p>No missing skills found.</p>"
                        }

                    </div>

                </div>


            </div>

            <button
                class="primary-button"
                id="goToResourcesButton"
                style="margin-top:25px;"
            >
                Explore Learning Resources →
            </button>

        </div>

    `;


    // Update Dashboard Overview statistics
    document.getElementById("careerMatch").textContent =
        `${percentage.toFixed(2)}%`;

    document.getElementById("careerName").textContent =
        document.getElementById("careerSelect")
            .selectedOptions[0].textContent;

    document.getElementById("completedSkills").textContent =
        matchedSkills.length;

    document.getElementById("totalSkills").textContent =
        data.total_required_skills || (matchedSkills.length + missingSkills.length);
    
    // Display recently updated skills
    const recentSkills = JSON.parse(
        localStorage.getItem("recently_updated_skills") || "[]"
    );

    const recentSkillsContainer = document.getElementById("recentSkills");

    if (recentSkillsContainer) {
        recentSkillsContainer.innerHTML = recentSkills.length
    ? `
        <div class="recent-skills-list">
            ${recentSkills.map(skill => `
                <span class="recent-skill-tag">
                    <span class="skill-check">✓</span>
                    ${escapeHTML(skill)}
                </span>
            `).join("")}
        </div>
        <p class="recent-skills-note">
            Keep building your career skills!
        </p>
    `
    : `<p class="empty-skills">No skills added yet.</p>`;
}
   // Make analysis results visible
if (results) {
    results.style.display = "block";
    results.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}
    document.getElementById("goToResourcesButton").addEventListener(
        "click",
        function () {
            showPage("resources");
        }
    );
}
async function loadSavedStudentAnalysis() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        console.log("No login token found.");
        return null;
    }

    try {
        const response = await fetch(`${API_URL}/student-analysis`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
            
        });
        console.log("Student analysis status:", response.status);

if (!response.ok) {
    console.log(
        "Student analysis error:",
        await response.clone().text()
    );
}

        if (response.status === 401) {
            console.error("Login token expired or invalid. Please log in again.");
            return null;
        }

        if (!response.ok) {
            throw new Error("Unable to load saved analysis.");
        }

        const data = await response.json();

        if (!data.has_analysis) return null;

        localStorage.setItem("selected_role_id", String(data.role_id));
        localStorage.setItem(
            "entered_student_skills",
            (data.student_skills || []).join(", ")
        );

        localStorage.setItem("matched_skills", JSON.stringify(data.matched_skills || []));
        localStorage.setItem("missing_skills", JSON.stringify(data.missing_skills || []));
        localStorage.setItem("recently_updated_skills", JSON.stringify(data.student_skills || []));
        localStorage.setItem("total_required_skills", String(data.total_required_skills || 0));
        localStorage.setItem("saved_match_percentage", String(data.match_percentage || 0));

        return data;

    } catch (error) {
        console.error("Saved analysis loading error:", error);
        return null;
    }
}
// Load saved analysis and open Skill Analysis first
async function initializeDashboard() {

    // Load available job roles
    await loadJobRoles();

    // Fetch previously saved analysis
    const savedAnalysis = await loadSavedStudentAnalysis();
    console.log("Saved analysis:", savedAnalysis);
    console.log("Dashboard page:", document.getElementById("dashboardPage"));
    console.log("Analysis page:", document.getElementById("analysisPage"));

    if (savedAnalysis) {

        const categorySelect =
            document.getElementById("categorySelect");

        const careerSelect =
            document.getElementById("careerSelect");

        const skillsInput =
            document.getElementById("studentSkills");

        // Restore selected career
        const savedRole = allRoles.find(
            role =>
                String(role.role_id) === String(savedAnalysis.role_id)
        );

        if (savedRole) {

            categorySelect.value = savedRole.sector;

            updateCareerOptions(savedRole.sector);

            careerSelect.value = String(savedAnalysis.role_id);
        }

        // Restore previously entered skills
        if (skillsInput) {
            skillsInput.value =
                (savedAnalysis.student_skills || []).join(", ");
        }
    }

    // Always open Skill Analysis after login
    // Open saved analysis results when available
if (savedAnalysis) {
    displayAnalysisResults(savedAnalysis);
    showPage("dashboard");
} else {
    showPage("analysis");
}
}


initializeDashboard();


// =====================================
// MY PROFILE
// =====================================

const profileContent = document.getElementById("profileContent");

if (student) {

    profileContent.innerHTML = `

        <div class="panel">

            <h3>Personal Information</h3>

            <div style="padding:20px 0;">

                <p>
                    <strong>Full Name:</strong>
                    ${escapeHTML(student.name)}
                </p>

                <p style="margin-top:15px;">
                    <strong>Email:</strong>
                    ${escapeHTML(student.email)}
                </p>

                <p style="margin-top:15px;">
                    <strong>Student ID:</strong>
                    ${student.student_id}
                </p>

            </div>

        </div>

    `;

}

// =====================================
// SETTINGS
// =====================================

document.getElementById("settingsContent").innerHTML = `

    <div class="panel">

        <h3>Account Settings</h3>

        <p style="margin-top:15px; color:#858ba1;">
            Your account is currently active.
        </p>

        <button
            class="primary-button"
            id="settingsLogout"
            style="margin-top:20px;"
        >
            Log Out
        </button>

    </div>

`;

// =====================================
// LEARNING RESOURCES
// =====================================

async function loadLearningResources() {

    const resourcesContent =
        document.getElementById("resourcesContent");

    const missingSkills = JSON.parse(
        localStorage.getItem("missing_skills") || "[]"
    );

    if (missingSkills.length === 0) {

        resourcesContent.innerHTML = `
            <div class="panel">
                <h3>No skill gaps found yet</h3>
                <p>
                    Complete your Skill Analysis first.
                    Your recommended learning resources
                    will appear here.
                </p>
                <button class="primary-button"
                    onclick="showPage('analysis')">
                    Start Skill Analysis →
                </button>
            </div>
        `;

        return;
    }

    resourcesContent.innerHTML = `
        <p style="color:#858398; margin-bottom:20px;">
            Recommended learning resources based on
            your identified skill gaps.
        </p>
        <div id="skillResourceList"></div>
    `;

    const skillResourceList =
        document.getElementById("skillResourceList");

    for (const skill of missingSkills) {
        const displaySkill = skill.replace(/\b\w/g, char => char.toUpperCase());

        const skillSection = document.createElement("div");

        skillSection.className = "panel";

        skillSection.innerHTML = `
            <h2>${escapeHTML(displaySkill)}</h2>
            <p style="color:#858398; font-size:12px;">
            Resources to help you learn ${escapeHTML(displaySkill)}.
            </p>
            <div class="resource-loading">
                Loading resources...
            </div>
        `;

        skillResourceList.appendChild(skillSection);

        try {

            const response = await fetch(
                `${API_URL}/resources/${encodeURIComponent(skill)}`
            );

            if (!response.ok) {
                throw new Error("Unable to fetch resources.");
            }

            const data = await response.json();

            const loading =
                skillSection.querySelector(".resource-loading");

            if (!data.resources || data.resources.length === 0) {

                loading.textContent =
                    "No learning resources available for this skill.";

                continue;
            }

            loading.innerHTML = "";

            data.resources.forEach(resource => {

                const resourceCard = document.createElement("div");

                resourceCard.className = "resource-item";

                const resourceURL = String(resource.resource_url || "");

                const safeURL = /^https?:\/\//i.test(resourceURL)
                    ? resourceURL
                    : "";

                resourceCard.innerHTML = `
                    <div class="resource-details">

                        <span class="resource-type">
                            ${escapeHTML(resource.resource_type)}
                        </span>

                        <h3>
                            ${escapeHTML(resource.resource_title)}
                        </h3>

                        <p>
                            ${escapeHTML(resource.platform)}
                        </p>

                    </div>

                    ${
                        safeURL
                        ? `<a href="${escapeHTML(safeURL)}"
                             target="_blank"
                             rel="noopener noreferrer"
                             class="resource-link">
                             Start Learning →
                           </a>`
                        : `<span>Link unavailable</span>`
                    }
                `;

                loading.appendChild(resourceCard);

            });

        }

        catch (error) {

            skillSection.querySelector(".resource-loading")
                .textContent =
                "Could not load resources. Please try again.";
            console.error(error);
        }
    }
}

// =====================================
// LOGOUT
// =====================================

function logoutStudent() {

    localStorage.removeItem("access_token");

    localStorage.removeItem("student");

    localStorage.removeItem("selected_role_id");

    window.location.href = "index.html";
}

document.getElementById("logoutButton").addEventListener(
    "click",
    logoutStudent
);

document.getElementById("settingsLogout").addEventListener(
    "click",
    logoutStudent
);