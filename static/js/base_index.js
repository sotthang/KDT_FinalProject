// csrf
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

function scrollTopFixed() {
  window.scrollTo(0, 0);
}

var weatherIcon = {
  '01': 'fas fa-sun',
  '02': 'fas fa-cloud-sun',
  '03': 'fas fa-cloud',
  '04': 'fas fa-cloud-meatball',
  '09': 'fas fa-cloud-sun-rain',
  '10': 'fas fa-cloud-showers-heavy',
  '11': 'fas fa-poo-storm',
  '13': 'far fa-snowflake',
  '50': 'fas fa-smog',
};

function getWeatherData(lat, lon) {
  var apiURI = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=b601f3a3c62f1f902a1a11a92d60a81d&lang=kr&units=metric`;

  $.ajax({
    url: apiURI,
    dataType: 'json',
    type: 'GET',
    async: 'false',
    success: function (resp) {
      var $Icon = resp.weather[0].icon.substr(0, 2);
      var $weather_description = resp.weather[0].main;
      var $Temp = Math.floor(resp.main.temp) + '°C';
      var $temp_min = '&nbsp;&nbsp;' + Math.floor(resp.main.temp_min) + '°C';
      var $temp_max = '&nbsp;&nbsp;' + Math.floor(resp.main.temp_max) + '°C';

      $('.weather_icon').empty();
      $('.weather_description').empty();
      $('.current_temp').empty();
      $('.temp_min').empty();
      $('.temp_max').empty();

      $('.weather_icon').append(
        '<i class="' + weatherIcon[$Icon] + ' fa-2x"></i>'
      );
      $('.weather_description').prepend($weather_description);
      $('.current_temp').prepend($Temp);
      $('.temp_min').append($temp_min);
      $('.temp_max').append($temp_max);
    },
  });
}

var lat = 37.5326;
var lon = 127.024612;
getWeatherData(lat, lon);

function success(position) {
  var lat = position.coords.latitude;
  var lon = position.coords.longitude;
  getWeatherData(lat, lon);
}

navigator.geolocation.getCurrentPosition(success);

document.addEventListener('DOMContentLoaded', function() {
  document.querySelector('body').addEventListener('click', function (e) {
    var target = e.target;

    // 즐겨찾기
    if (target.matches('#star')) {
      e.preventDefault();

      var starButton = target;
      var planetName = starButton.dataset.planetName;
      var value = starButton.value;

      axios({
        url: '/planets/' + planetName + '/star/',
        method: 'POST',
        data: value,
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')
            .value,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            if (response.data.star) {
              target.classList.remove('fa-regular');
              target.classList.add('fa-solid');
            } else {
              target.classList.remove('fa-solid');
              target.classList.add('fa-regular');
            }
          } else {
            console.error('Star failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }
  });

  document.querySelector('body').addEventListener('submit', function (e) {
    var target = e.target;

    // 게시글 생성
    if (target.matches('#post-form')) {
      e.preventDefault();

      var form = e.target;
      var planetName = form.dataset.planetName;
      var formData = new FormData(form);
      formData.append('csrfmiddlewaretoken', csrftoken);
      var redirectUrl = '/planets/' + planetName + '/';
      var encodedPlanetName = encodeURIComponent(planetName);
      var urlPattern = new RegExp('^/planets/' + encodedPlanetName + '/$');

      axios({
        method: 'post',
        url: '/planets/' + planetName + '/create/',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
        .then(function (response) {
          if (
            response.data.success &&
            urlPattern.test(window.location.pathname)
          ) {
            var post_pk = response.data.post_pk;
            var postList = document.getElementById('post-list');
            var newPostContainer = createpostContainer(
              response.data.profile_image_url,
              response.data.nickname,
              response.data.created_time,
              response.data.content,
              response.data.tags,
              post_pk,
              response.data.image_url,
              response.data.user,
              response.data.votetopics,
              // emote heart, thumbsup, thumbsdown은 새 게시물에서 0으로 시작
              0,
              0,
              0,
              response.data.vote_count,
              response.data.voted
            );

            postList.insertBefore(newPostContainer, postList.children[1]);
            form.reset();
          } else if (
            response.data.success &&
            !urlPattern.test(window.location.pathname)
          ) {
            window.location.href = redirectUrl;
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 메모 생성
    else if (target.matches('#create-memo-form')) {
      e.preventDefault();

      var createForm = target;
      var indexmemoDivs = document.querySelectorAll('#index-memo');
      var planetName = createForm.dataset.planetName;
      var formData = new FormData(createForm);

      axios({
        url: '/planets/' + planetName + '/memo/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')
            .value,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            var memo = response.data.memo;

            // 각 index-memo 요소에 대해 작업 수행
            indexmemoDivs.forEach(function (indexmemoDiv) {
              var memoDiv = document.createElement('div');
              memoDiv.id = 'memo';
              var memocontentDiv = document.createElement('div');
              memocontentDiv.id = 'memo-content';
              memocontentDiv.classList.add('ml-3', 'mt-3');
              memocontentDiv.style.wordBreak = 'break-all';
              memocontentDiv.style.maxWidth = '90%';
              memocontentDiv.style.overflow = 'auto';
              memocontentDiv.style.maxHeight = '4.5em';
              memocontentDiv.textContent = memo;
              var formElement = document.createElement('form');
              formElement.id = 'update-memo-form';
              formElement.setAttribute('data-planet-name', planetName);
              memoDiv.append(formElement);
              var button = document.createElement('button');
              button.id = 'update-memo-button';
              button.innerHTML =
                "<span class='material-symbols-outlined'>edit</span>";
              button.classList.add('absolute', 'bottom-2', 'right-2');
              button.setAttribute('data-planet-name', planetName);
              formElement.append(button);
              memoDiv.append(memocontentDiv);
              memoDiv.append(formElement);
              indexmemoDiv.querySelector('#create-memo-form').remove();
              indexmemoDiv.append(memoDiv);
            });
          } else {
            console.error('Memo failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 메모 수정 form
    else if (target.matches('#update-memo-form')) {
      e.preventDefault();

      var updateForm = target;
      var updatebutton = target;
      var indexmemoDiv = updateForm.closest('#index-memo');
      var planetName = updatebutton.dataset.planetName;
      var formData = new FormData(updateForm);

      axios({
        url: '/planets/' + planetName + '/memo/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')
            .value,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            indexmemoDiv.querySelector('#memo').style.display = 'none';
            var memoform = response.data.memoform;
            var formContainer = document.createElement('div');
            formContainer.innerHTML = memoform;
            var formElement = document.createElement('form');
            formElement.id = 'edit-memo-form';
            formElement.setAttribute('data-planet-name', planetName);
            formElement.appendChild(formContainer);
            var submitButton = document.createElement('button');
            submitButton.id = 'edit-post-button';
            submitButton.classList.add('absolute', 'bottom-2', 'right-2');
            submitButton.innerHTML =
              '<span class="material-symbols-outlined">edit</span>';
            submitButton.type = 'submit';
            formElement.append(submitButton);
            indexmemoDiv.append(formElement);
          } else {
            console.error('Memo failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 메모 수정 처리
    else if (target.matches('#edit-memo-form')) {
      e.preventDefault();

      var updateForm = target;
      var updatebutton = target;
      var indexmemoDivList = document.querySelectorAll('#index-memo');
      var planetName = updatebutton.dataset.planetName;
      var formData = new FormData(updateForm);

      axios({
        url: '/planets/' + planetName + '/memo/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')
            .value,
        },
      })
        .then(function (response) {
          if (response.data.success && response.data.memo) {
            indexmemoDivList.forEach(function (indexmemoDiv) {
              var memoDiv = indexmemoDiv.querySelector('#memo');
              memoDiv.style.display = 'block';
              document
                .querySelectorAll('#memo-content')
                .forEach((e) => (e.textContent = response.data.memo));
              document
                .querySelectorAll('#edit-memo-form')
                .forEach((e) => e.remove());
              document
                .querySelectorAll('#edit-memo-button')
                .forEach((e) => e.remove());
            });
          } else {
            indexmemoDivList.forEach(function (indexmemoDiv) {
              indexmemoDiv.innerHTML = '';
              // create-memo-form 생성
              var createForm = document.createElement('form');
              createForm.id = 'create-memo-form';
              createForm.setAttribute('data-planet-name', planetName);

              // memo 입력 필드 생성
              var memoInput = document.createElement('input');
              memoInput.type = 'text';
              memoInput.name = 'memo';
              memoInput.classList.add(
                'form-input',
                'mt-1',
                'rounded-md',
                'border-yellow-100',
                'bg-yellow-100',
                'focus:outline-none',
                'focus:ring-0',
                'appearance-none',
                'placeholder-gray-600',
                'placeholder:text-sm'
              );
              memoInput.style.width = '100%';
              memoInput.style.height = '80%';
              memoInput.placeholder = '메모 작성';
              memoInput.id = 'id_memo';

              // create-memo-button 생성
              var createButton = document.createElement('button');
              createButton.classList.add('absolute', 'bottom-2', 'right-2');
              createButton.id = 'create-memo-button';

              var spanElement = document.createElement('span');
              spanElement.classList.add('material-symbols-outlined');
              spanElement.textContent = 'edit';

              createButton.appendChild(spanElement);

              // create-memo-form에 memo 입력 필드와 create-memo-button 추가
              createForm.appendChild(memoInput);
              createForm.appendChild(createButton);

              // index-memo에 create-memo-form 추가
              indexmemoDiv.appendChild(createForm);
            });
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }
  });
});

// vote
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
