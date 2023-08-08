const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
const modalButton = document.getElementById('modalButton');
const inviteModal = document.getElementById('inviteModal');
const inviteForm = document.getElementById('inviteForm');
const errorText = document.getElementById('errorText');

modalButton.addEventListener('click', function() {
  errorText.classList.add('hidden');
});

// 다른 창 클릭 시 모달 닫기
window.addEventListener('click', function(event) {
  if (event.target === inviteModal) {
    inviteModal.classList.add('hidden');
    errorText.classList.add('hidden');
  }
});


inviteForm.addEventListener('submit', function(event) {
  // 기본 동작 방지
  event.preventDefault();
  
  // 폼 데이터 가져오기
  const userInput = inviteForm.querySelector('input[name="invitation_code"]').value;

  // 폼 데이터 처리
  // 예: 서버로 전송하여 처리하거나, 다른 동작 수행 등

  // AJAX 요청 보내기
  fetch('/planets/invite_create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({
      user_input: userInput
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.result === false) {
      // 초대코드가 유효하지 않은 경우에 대한 처리
      errorText.classList.remove('hidden');
      errorText.style.color = 'red';
      errorText.textContent = '초대코드가 유효하지 않습니다.';
    } else if (data.result === true) {
    errorText.classList.add('hidden');
    window.location.href = '/planets/invite_check/' + data.invite_code + '/';

    }
  })
  .catch(error => {
    // 에러 처리
    console.error(error);
  });
});

// 행성 소개글 3줄 넘어갈 때 처리
document.addEventListener('DOMContentLoaded', function() {
  const planets = document.querySelectorAll('[id^="description-"]');
  const moreButtons = document.querySelectorAll('[id^="moreButton-"]');
  const clickCounts = {}; // 개별 행성의 클릭 횟수를 저장하는 객체

  for (let i = 0; i < planets.length; i++) {
    const planet = planets[i];
    const planetId = planet.id;
    const moreButton = moreButtons[i];
    clickCounts[planetId] = 0; // 초기 클릭 횟수를 0으로 설정

    moreButton.addEventListener('click', function() {
      const planetElement = document.getElementById(planetId);
      planetElement.classList.toggle('clamp-3-lines');

      const hasMoreContent = planetElement.scrollHeight > planetElement.clientHeight;

      clickCounts[planetId]++; // 해당 행성의 클릭 횟수 증가

      if (clickCounts[planetId] % 2 === 0) {
        moreButton.textContent = '더보기'; // 클릭 횟수가 짝수인 경우 '더보기'로 설정
      } else {
        moreButton.textContent = '감추기'; // 클릭 횟수가 홀수인 경우 '감추기'로 설정
      }

      console.log(clickCounts);
    });

    const planetElement = document.getElementById(planetId);
    const hasMoreContentInitially = planetElement.scrollHeight > planetElement.clientHeight;

    if (!hasMoreContentInitially) {
      moreButton.style.display = 'none';
    }
  }

  window.addEventListener('resize', function() {
    for (let i = 0; i < planets.length; i++) {
      const planet = planets[i];
      const planetId = planet.id;
      const planetElement = document.getElementById(planetId);
      const moreButton = moreButtons[i];

      const hasMoreContent = planetElement.scrollHeight > planetElement.clientHeight;

      if (hasMoreContent && planetElement.classList.contains('clamp-3-lines')) {
        moreButton.style.display = 'inline';
      } else {
        moreButton.style.display = 'none';
      }
    }
  });
});



// main comtent 바 이동
const btn1 = document.getElementById('btn1');
const sec1 = document.getElementById('sec1');

btn1.addEventListener('click', () => {
  window.scrollBy({top: sec1.getBoundingClientRect().top-180, behavior: 'smooth'});
});

const btn2 = document.getElementById('btn2');
const sec2 = document.getElementById('sec2');

btn2.addEventListener('click', () => {
  window.scrollBy({top: sec2.getBoundingClientRect().top-180, behavior: 'smooth'});
});

const btn3 = document.getElementById('btn3');
const sec3 = document.getElementById('sec3');

btn3.addEventListener('click', () => {
  window.scrollBy({top: sec3.getBoundingClientRect().top-180, behavior: 'smooth'});
});

const btn4 = document.getElementById('btn4');
const sec4 = document.getElementById('sec4');

btn4.addEventListener('click', () => {
  window.scrollBy({top: sec4.getBoundingClientRect().top-180, behavior: 'smooth'});
});

// 클릭 시 아코디언 열리도록 설정
document.getElementById("btn1").addEventListener("click", function() {
  var accordionBody = document.getElementById("accordion-flush-body-1");
  if (accordionBody.style.display === "none" || accordionBody.style.display === "") {
    accordionBody.style.display = "block";
  } else {
    accordionBody.style.display = "none";
  }
});

document.getElementById("btn2").addEventListener("click", function() {
  var accordionBody = document.getElementById("accordion-flush-body-2");
  if (accordionBody.style.display === "none" || accordionBody.style.display === "") {
    accordionBody.style.display = "block";
  } else {
    accordionBody.style.display = "none";
  }
});

document.getElementById("btn3").addEventListener("click", function() {
  var accordionBody = document.getElementById("accordion-flush-body-3");
  if (accordionBody.style.display === "none" || accordionBody.style.display === "") {
    accordionBody.style.display = "block";
  } else {
    accordionBody.style.display = "none";
  }
});
