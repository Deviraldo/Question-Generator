// ============================================
// API URL
// ============================================

const API_URL =
    "http://127.0.0.1:8000";


// ============================================
// GET HTML ELEMENTS
// ============================================

const topic =
    document.getElementById("topic");

const numberOfQuestions =
    document.getElementById("numberOfQuestions");

const difficulty =
    document.getElementById("difficulty");

const questionType =
    document.getElementById("questionType");

const additionalInstructions =
    document.getElementById(
        "additionalInstructions"
    );

const generateButton =
    document.getElementById(
        "generateButton"
    );

const loading =
    document.getElementById("loading");

const errorMessage =
    document.getElementById(
        "errorMessage"
    );

const resultSection =
    document.getElementById(
        "resultSection"
    );

const questionsOutput =
    document.getElementById(
        "questionsOutput"
    );

const characterCount =
    document.getElementById(
        "characterCount"
    );


// ============================================
// CHARACTER COUNTER
// ============================================

additionalInstructions.addEventListener(
    "input",
    function () {

        const count =
            additionalInstructions.value.length;

        characterCount.textContent =
            `${count} / 2000`;

    }
);


// ============================================
// GENERATE QUESTIONS
// ============================================

async function generateQuestions() {

    // Get values

    const topicValue =
        topic.value.trim();

    const numberValue =
        Number(numberOfQuestions.value);

    const difficultyValue =
        difficulty.value;

    const questionTypeValue =
        questionType.value;

    const instructionsValue =
        additionalInstructions.value.trim();


    // ========================================
    // VALIDATION
    // ========================================

    if (!topicValue) {

        showError(
            "Please enter a topic."
        );

        return;
    }


    if (
        numberValue < 1 ||
        numberValue > 20
    ) {

        showError(
            "Please select between 1 and 20 questions."
        );

        return;
    }


    // ========================================
    // RESET UI
    // ========================================

    hideError();

    resultSection.classList.add(
        "hidden"
    );

    loading.classList.remove(
        "hidden"
    );

    generateButton.disabled =
        true;


    try {

        // ====================================
        // SEND REQUEST TO FASTAPI
        // ====================================

        const response = await fetch(
            `${API_URL}/generate-questions`,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    topic:
                        topicValue,

                    number_of_questions:
                        numberValue,

                    difficulty:
                        difficultyValue,

                    question_type:
                        questionTypeValue,

                    additional_instructions:
                        instructionsValue

                })

            }
        );


        // ====================================
        // GET RESPONSE
        // ====================================

        const data =
            await response.json();


        // ====================================
        // CHECK ERROR
        // ====================================

        if (!response.ok) {

            throw new Error(

                data.detail ||
                "Failed to generate questions."

            );

        }


        // ====================================
        // DISPLAY QUESTIONS
        // ====================================

        questionsOutput.textContent =
            data.questions;


        resultSection.classList.remove(
            "hidden"
        );

    }


    catch (error) {

        console.error(error);

        showError(

            error.message ||
            "Could not connect to the backend."

        );

    }


    finally {

        loading.classList.add(
            "hidden"
        );

        generateButton.disabled =
            false;

    }

}


// ============================================
// COPY QUESTIONS
// ============================================

async function copyQuestions() {

    const questions =
        questionsOutput.textContent;


    if (!questions) {

        return;

    }


    try {

        await navigator.clipboard.writeText(
            questions
        );


        const button =
            document.getElementById(
                "copyButton"
            );


        const originalText =
            button.textContent;


        button.textContent =
            "Copied!";


        setTimeout(
            function () {

                button.textContent =
                    originalText;

            },
            1500
        );

    }


    catch (error) {

        console.error(
            "Copy failed:",
            error
        );

    }

}


// ============================================
// SHOW ERROR
// ============================================

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );

}


// ============================================
// HIDE ERROR
// ============================================

function hideError() {

    errorMessage.classList.add(
        "hidden"
    );

}