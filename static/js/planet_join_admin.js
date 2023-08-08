const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
const planetName = document.querySelector('.planet_name').innerHTML
    
const joinConfirms = document.querySelectorAll('.join-confirm');

joinConfirms.forEach((confirm) => {
  confirm.addEventListener('submit', (event) => {
    event.preventDefault();
    const userpk = event.target.dataset.userPk;

    Swal.fire({
      title: '승인하시겠습니까?',
      text: "승인하면 유저가 행성에 들어올 수 있습니다",
      icon: 'info',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: '승인합니다',
      cancelButtonText: '아니오'
    }).then((result) => {
      if (result.isConfirmed) {
        axios({
          method: 'post',
          url: `/planets/${planetName}/admin/join/${userpk}/confirm/`,
          headers: { 'X-CSRFToken': csrftoken },
        })
          .then(function (response) {
            if (response.data.success) {
              const confirmDiv = document.getElementById(`join-form-${userpk}`);
              confirmDiv.remove();
              Swal.fire({
                icon: 'success',
                title: '가입 완료!',
                text: '이 유저는 이제 행성에 들어올 수 있습니다!',
                timer: 2000,
                showConfirmButton: false
              });
              const confirmList = document.querySelector('.confirm-list');
              if (confirmList.textContent.trim() === '') {
                const noList = document.createElement('p');
                noList.textContent = '가입 대기중인 유저가 없습니다.';
                noList.classList.add('mt-10', 'text-center', 'text-gray-200');
                confirmList.appendChild(noList);
              }
            }
          })
          .catch((error) => {
            console.log(error.response);
          });
      }
    });
  });
});


const joinRejects = document.querySelectorAll('.join-reject');

joinRejects.forEach((reject) => {
  reject.addEventListener('submit', (event) => {
    event.preventDefault();
    const userpk = event.target.dataset.userPk;

    Swal.fire({
      title: '거절하시겠습니까?',
      text: '거절하면 이 유저는 행성에 들어올 수 없습니다',
      icon: 'error',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: '거절합니다',
      cancelButtonText: '아니오'
    }).then((result) => {
      if (result.isConfirmed) {
        axios({
          method: 'post',
          url: `/planets/${planetName}/admin/join/${userpk}/reject/`,
          headers: { 'X-CSRFToken': csrftoken },
        })
          .then(function (response) {
            if (response.data.success) {
              const confirmDiv = document.getElementById(`join-form-${userpk}`);
              confirmDiv.remove();
              Swal.fire({
                icon: 'success',
                title: '거절했습니다',
                text: '이 유저는 행성에 들어올 수 없습니다!',
                timer: 2000,
                showConfirmButton: false
              });
              const confirmList = document.querySelector('.confirm-list');
              if (confirmList.textContent.trim() === '') {
                const noList = document.createElement('p');
                noList.textContent = '가입 대기중인 유저가 없습니다.';
                noList.classList.add('mt-10', 'text-center', 'text-gray-200');
                confirmList.appendChild(noList);
              }
            }
          })
          .catch((error) => {
            console.log(error.response);
          });
      }
    });
  });
});

