const API_URL = "http://127.0.0.1:8000";

const categoryConfig = {
    technology: {
        title: "Technology & IT",
        sectors: ["Technology"]
    },

    design: {
        title: "Design & Creative",
        sectors: ["Creative & Media"]
    },

    marketing: {
        title: "Marketing & Growth",
        sectors: ["Business, Sales & People"]
    },

    business: {
        title: "Business & Finance",
        sectors: ["Business, Sales & People", "Finance & Insurance"]
    },

    soft: {
        title: "Soft Skills",
        sectors: ["Business, Sales & People"]
    },

    government: {
        title: "Government & Vocational",
        sectors: ["Education & Public Service"]
    },

    future: {
        title: "Future & Emerging",
        sectors: ["Technology", "Green Energy & Environment"]
    },

    digital: {
        title: "Digital Foundations",
        sectors: ["Technology"]
    }
};

const params = new URLSearchParams(window.location.search);
const selectedCategory = params.get("category");

const category = categoryConfig[selectedCategory];

const categoryTitle = document.getElementById("categoryTitle");
const jobsList = document.getElementById("jobsList");
const searchInput = document.getElementById("searchInput");

let allJobs = [];

if (!category) {
    categoryTitle.textContent = "Category Not Found";
    jobsList.innerHTML = "<p>Please select a valid career category.</p>";
} else {
    categoryTitle.textContent = category.title;
    loadJobs();
}

async function loadJobs() {
    try {
        const response = await fetch(`${API_URL}/roles`);

        if (!response.ok) {
            throw new Error("Unable to fetch job roles.");
        }

        const data = await response.json();

        allJobs = data.roles.filter(role =>
            category.sectors.includes(role.sector)
        );

        displayJobs(allJobs);

    } catch (error) {
        console.error(error);

        jobsList.innerHTML = `
            <p>Unable to load job roles. 
            Please make sure your FastAPI server is running.</p>
        `;
    }
}

function displayJobs(jobs) {
    jobsList.innerHTML = "";

    if (jobs.length === 0) {
        jobsList.innerHTML = "<p>No job roles found.</p>";
        return;
    }

    jobs.forEach(job => {
        const jobCard = document.createElement("div");
        jobCard.className = "job-card";

        jobCard.innerHTML = `
            <h3>${job.job_role}</h3>
        `;

        jobsList.appendChild(jobCard);
    });
}

searchInput.addEventListener("input", function () {
    const searchText = this.value.toLowerCase();

    const filteredJobs = allJobs.filter(job =>
        job.job_role.toLowerCase().includes(searchText)
    );

    displayJobs(filteredJobs);
});
