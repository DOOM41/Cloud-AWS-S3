const uploadForm = document.getElementById("uploadForm");
const HOST = 'http://127.0.0.1:8000';


async function sendChunk(file, chunk, chunkIndex, totalChunks) {
    const formData = new FormData();
    formData.append("file", chunk, file.name);

    formData.append("chunk_index", chunkIndex);
    formData.append("total_chunks", totalChunks);

    try {
        const response = await fetch(HOST + "/upload", {
            method: "POST",
            body: formData,
            cors: "no-cors",
        });

        if (response.ok) {
            console.log(`Chunk ${chunkIndex} uploaded successfully!`);
        } else {
            console
            console.error(`Error uploading chunk ${chunkIndex}: ${response.statusText}`);
        }
    } catch (error) {
        console.error(`Error uploading chunk ${chunkIndex}: ${error}`);
    }
}

function sliceFile(file, chunksAmount) {
    var byteIndex = 0;
    var chunks = [];

    for (var i = 0; i < chunksAmount; i += 1) {
        var byteEnd = Math.ceil((file.size / chunksAmount) * (i + 1));
        chunks.push(file.slice(byteIndex, byteEnd));
        byteIndex += (byteEnd - byteIndex);
    }

    return chunks;
}

async function uploadFileChunks(file) {
    let parts = file.size / (100 * Math.pow(1024, 2));
    parts = Math.ceil(parts);
    if (parts <= 1){
        parts = 4;
    }
    const chunks = sliceFile(file, parts);
    const totalChunks = chunks.length;
    try {
        console.log(`Uploading file ${file.name} in ${totalChunks} chunks...`);
        await sendChunk(file, chunks[0], 1, totalChunks);
        const promises = chunks.slice(1, -1).map((chunk, i) => {
            return sendChunk(file, chunk, i + 2, totalChunks);
        });
        await Promise.all(promises);
        await sendChunk(file, chunks[totalChunks - 1], totalChunks, totalChunks);
        console.log(`File ${file.name} uploaded successfully!`);
    } catch (error) {
        console.error(`Error uploading file ${file.name}: ${error}`);
    }
}

uploadForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    uploadFileChunks(file);
});