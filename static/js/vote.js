// // 이미지를 눌러야 투표 폼이 생김
// const voteToggle = document.getElementById('vote-toggle');
// const voteTopicsContainer = document.getElementById('vote-topics-container');

// voteToggle.addEventListener('click', function () {
//   if (voteTopicsContainer.style.display === 'none') {
//     voteTopicsContainer.style.display = 'block';
//   } else {
//     voteTopicsContainer.style.display = 'none';
//   }
// });

// const plusButton = document.getElementById('plus-button');
// const voteTopics = document.getElementById('vote-topics');

// plusButton.addEventListener('click', function () {
//   event.preventDefault(); // 폼 제출 방지
//   const newTopicInput = document.createElement('input');
//   newTopicInput.type = 'text';
//   newTopicInput.name = 'title';
//   newTopicInput.classList.add(
//     'block',
//     'mt-2',
//     'w-full',
//     'bg-[#101013]',
//     'text-white',
//     'rounded-lg',
//     'py-2',
//     'px-3'
//   );

//   const deleteButton = document.createElement('button');
//   deleteButton.textContent = '-';
//   deleteButton.setAttribute('class', 'delete-button');
//   deleteButton.addEventListener('click', function () {
//     voteTopics.removeChild(newTopicInput.parentNode);
//   });

//   const inputWrapper = document.createElement('div');
//   inputWrapper.setAttribute('class', 'vote-topic-input');
//   inputWrapper.appendChild(newTopicInput);
//   inputWrapper.appendChild(deleteButton);

//   voteTopics.appendChild(inputWrapper);
// });

const voteToggle = document.getElementById('vote-toggle');
const voteTopicsContainer = document.getElementById('vote-topics-container');
const voteTopics = document.getElementById('vote-topics');

voteToggle.addEventListener('click', function () {
  const computedStyle = window.getComputedStyle(voteTopicsContainer);
  if (computedStyle.display === 'none') {
    voteTopicsContainer.style.display = 'block';
  } else {
    // 이미지를 클릭하여 폼을 숨기는 경우, 첫 번째 주제를 제외한 나머지 주제를 삭제합니다.
    const topicInputs = voteTopics.querySelectorAll('.vote-topic-input');
    for (let i = topicInputs.length - 1; i > 0; i--) {
      topicInputs[i].remove();
    }
    voteTopicsContainer.style.display = 'none';
  }
});

const plusButton = document.getElementById('plus-button');

plusButton.addEventListener('click', function () {
  event.preventDefault(); // 폼 제출 방지
  const newTopicInput = document.createElement('input');
  newTopicInput.type = 'text';
  newTopicInput.name = 'title';
  newTopicInput.classList.add(
    'block',
    'mt-2',
    'w-full',
    'bg-[#101013]',
    'text-white',
    'rounded-lg',
    'py-2',
    'px-3'
  );

  const deleteButton = document.createElement('button');
  deleteButton.textContent = '-';
  deleteButton.setAttribute('class', 'delete-button');
  deleteButton.addEventListener('click', function () {
    voteTopics.removeChild(newTopicInput.parentNode);
  });

  const inputWrapper = document.createElement('div');
  inputWrapper.setAttribute('class', 'vote-topic-input');
  inputWrapper.appendChild(newTopicInput);
  inputWrapper.appendChild(deleteButton);

  voteTopics.appendChild(inputWrapper);
});
