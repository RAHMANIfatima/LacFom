function displayFileName(input) {
  var fileName =
    input.files && input.files.length > 0 ? input.files[0].name : "";
  document.getElementById("file-name").textContent = fileName;
}
