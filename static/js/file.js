 const inputFile = document.getElementById('imagen');
  const fileNameSpan = document.getElementById('file-name');

  inputFile.addEventListener('change', () => {
    if (inputFile.files.length > 0) {
      fileNameSpan.textContent = inputFile.files[0].name;
    } else {
      fileNameSpan.textContent = 'Ningún archivo seleccionado';
    }
  });