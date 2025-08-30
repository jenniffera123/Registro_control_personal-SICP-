const inputFile = document.getElementById('imagen');
const inputFile2 = document.getElementById('firma_digital');

const fileNameSpan1 = document.getElementById('file-name-imagen');
const fileNameSpan2 = document.getElementById('file-name-firma');

inputFile.addEventListener('change', () => {
    if (inputFile.files.length > 0) {
      fileNameSpan1.textContent = inputFile.files[0].name;
    } else {
      fileNameSpan1.textContent = 'Ningún archivo seleccionado';
    }
});

inputFile2.addEventListener('change', () => {
    if (inputFile2.files.length > 0) {
      fileNameSpan2.textContent = inputFile2.files[0].name;
    } else {
      fileNameSpan2.textContent = 'Ningún archivo seleccionado';
    }
});
