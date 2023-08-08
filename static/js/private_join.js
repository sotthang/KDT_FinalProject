const modalButton = document.getElementById('modalButton');
const inviteModal = document.getElementById('inviteModal');
const inviteForm = document.getElementById('inviteForm');
const errorText = document.getElementById('errorText');

modalButton.addEventListener('click', function () {
  inviteModal.classList.toggle('hidden');
  errorText.classList.add('hidden');
});

// 다른 창 클릭 시 모달 닫기
window.addEventListener('click', function (event) {
  if (event.target === inviteModal) {
    inviteModal.classList.add('hidden');
    errorText.classList.add('hidden');
  }
});

inviteForm.addEventListener('submit', function (event) {
  // 기본 동작 방지
  event.preventDefault();

  // 폼 데이터 가져오기
  const userInput = inviteForm.querySelector('input[name="user_input"]').value;

  // 폼 데이터 처리
  // 예: 서버로 전송하여 처리하거나, 다른 동작 수행 등

  // AJAX 요청 보내기
  fetch('{% url "planets:invite_create" %}', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}',
    },
    body: JSON.stringify({
      user_input: userInput,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.result === false) {
        // 초대코드가 유효하지 않은 경우에 대한 처리
        errorText.classList.remove('hidden');
        errorText.style.color = 'red';
        errorText.textContent = '초대코드가 유효하지 않습니다.';
      } else if (data.result === true) {
        errorText.classList.add('hidden');
        window.location.href =
          '/planets/invite_check/' + data.invite_code + '/';
      }
    })
    .catch((error) => {
      // 에러 처리
      console.error(error);
    });
});
