document.addEventListener('DOMContentLoaded', function () {
  const addTermBtn = document.getElementById('add-term-btn');
  const termFieldsContainer = document.getElementById('term-fields-container');
  let termCount = 0;

  addTermBtn.addEventListener('click', function () {
    termCount++;

    const termField = document.createElement('div');
    termField.innerHTML = `

    <div class="my-5 flex gap-1 delete-term-btn">
      <label class="flex items-center"  for="term_content_${termCount}"> <span class="">약관 : </span> </label>
      <input type="text" class="rounded-md text-black w-4/5" id="term_content_${termCount}" name="term_content_${termCount}">
      <button type="button" class="my-auto justify-center flex items-center bg-red-400 rounded-lg delete-term-btn" style="width:30px; height:30px;" data-term-count="${termCount}">X</button>
      <br>
    </div>
    `;

    termFieldsContainer.appendChild(termField);
    document.getElementById('num-terms').value = termCount;
  });

  termFieldsContainer.addEventListener('click', function (event) {
    if (event.target.classList.contains('delete-term-btn')) {
      const termCount = event.target.getAttribute('data-term-count');
      const termField = document.getElementById(`term_content_${termCount}`).parentNode;
      termField.remove();
      document.getElementById('num-terms').value = termFieldsContainer.children.length;
    }
  });
});