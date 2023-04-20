const uploadForm = document.getElementById("uploadForm");

uploadForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    const url = "http://127.0.0.1:8000/upload";

    const formData = new FormData();
    formData.append("file", file, file.name);

    try {
        const response = await fetch(url, {
            method: "POST",
            cors: "no-cors",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
});