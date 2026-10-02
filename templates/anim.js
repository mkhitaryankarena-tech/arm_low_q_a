async function askQuestion() {

    const question =
        document.getElementById("question").value.trim();

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    const loading =
        document.getElementById("loading");

    const result =
        document.getElementById("result");

    loading.classList.remove("hidden");
    result.classList.add("hidden");

    try {

        const response = await fetch("/ask", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Request failed"
            );
        }

        document.getElementById("answer").textContent =
            data.answer;

        const sources =
            document.getElementById("sources");

        sources.innerHTML = "";

        data.sources.forEach(source => {

            const sourceElement =
                document.createElement("div");

            sourceElement.className = "source";

            sourceElement.textContent =
                "Հոդված " +
                source.article_number +
                " — " +
                source.title;

            sources.appendChild(sourceElement);
        });

        result.classList.remove("hidden");

    } catch (error) {

        document.getElementById("answer").textContent =
            "Error: " + error.message;

        result.classList.remove("hidden");

    } finally {

        loading.classList.add("hidden");
    }
}
function showTab(tabName) {

    const qaTab = document.getElementById("qa-tab");
    const benchmarkTab = document.getElementById("benchmark-tab");

    const buttons = document.querySelectorAll(".tab-button");

    qaTab.classList.remove("active");
    benchmarkTab.classList.remove("active");

    buttons.forEach(button => {
        button.classList.remove("active");
    });

    if (tabName === "qa") {
        qaTab.classList.add("active");
        buttons[0].classList.add("active");
    } else {
        benchmarkTab.classList.add("active");
        buttons[1].classList.add("active");
    }
}
async function runBenchmark() {

    const question = document
        .getElementById("benchmark-question")
        .value
        .trim();

    if (!question) {
        alert("Please enter a benchmark question.");
        return;
    }

    const loading =
        document.getElementById("benchmark-loading");

    const results =
        document.getElementById("benchmark-results");

    loading.classList.remove("hidden");
    results.innerHTML = "";

    try {

        const response = await fetch("/benchmark", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Benchmark request failed"
            );
        }

        console.log("Benchmark response:", data);

        displayBenchmarkResults(data);

    } catch (error) {

        results.innerHTML =
            "<p>Error: " + error.message + "</p>";

    } finally {

        loading.classList.add("hidden");
    }
}
function displayBenchmarkResults(data) {

    const container =
        document.getElementById("benchmark-results");

    container.innerHTML = "";

    const title = document.createElement("h2");
    title.textContent = "Benchmark Results";
    container.appendChild(title);

    const question = document.createElement("p");
    question.textContent =
        "Question: " + (data.question || "");

    container.appendChild(question);


    // -------------------------
    // PROVIDER RESULTS
    // -------------------------

    const results = data.results || [];

    results.forEach(item => {

        const card = document.createElement("div");
        card.className = "benchmark-card";

        const provider = document.createElement("h3");
        provider.textContent =
            (item.provider || "Unknown").toUpperCase();

        card.appendChild(provider);


        const status = document.createElement("p");
        status.textContent =
            "Status: " + (item.status || "unknown");

        card.appendChild(status);


        const answer = document.createElement("div");
        answer.className = "benchmark-answer";
        answer.textContent =
            item.answer || "No answer";

        card.appendChild(answer);


        if (item.latency_seconds !== undefined) {

            const latency = document.createElement("p");

            latency.textContent =
                "Time: " +
                item.latency_seconds +
                " seconds";

            card.appendChild(latency);
        }

        container.appendChild(card);
    });


    // -------------------------
    // RETRIEVED SOURCES
    // -------------------------

    if (data.sources && data.sources.length > 0) {

        const sourceTitle =
            document.createElement("h2");

        sourceTitle.textContent =
            "Retrieved Sources";

        container.appendChild(sourceTitle);


        data.sources.forEach(source => {

            const sourceElement =
                document.createElement("div");

            sourceElement.className =
                "source";

            sourceElement.textContent =
                "Հոդված " +
                source.article_number +
                " — " +
                source.title;

            container.appendChild(sourceElement);
        });
    }
}