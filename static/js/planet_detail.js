// var requestuser = '{{ request.user }}';
// var requestuser_nickname = '{{ user.nickname }}';
// var votetopicsDiv = document.getElementById('post-votetopics');
// if (votetopicsDiv.children.length === 0) {
//   votetopicsDiv.style.display = 'none';
// }

// 투표
function castVote(postPk, voteTitle) {
  var url = '/planets/post/' + postPk + '/' + voteTitle + '/';
  // AJAX 요청으로 투표 처리
  $.ajax({
    url: url,
    type: 'POST',
    data: {
      csrfmiddlewaretoken: csrftoken,
    },
    dataType: 'json',
    success: function (data) {
      // 투표 처리 후에 필요한 동작 수행
      // 예를 들어, 투표 수 업데이트 등
      window.location.reload(); // 페이지 새로고침
    },
    error: function (xhr, status, error) {
      // 투표 처리 실패 시에 대한 처리
      console.error('투표 실패:', error);
    },
  });
}

var planetName = document
  .getElementById('comment-create-form')
  .getAttribute('data-planet-name');
var postPk = document
  .getElementById('comment-create-form')
  .getAttribute('data-post-pk');

if (
  requestuser_nickname == document.getElementById('post-nickname').textContent
) {
  document
    .getElementById('dropdown-menu')
    .querySelector('li#dropdown-delete').style.display = 'block';
  document
    .getElementById('dropdown-menu')
    .querySelector('li#dropdown-update').style.display = 'block';
}

// comments, recomments rendering 비동기 처리
function loadComments() {
  $.ajax({
    url: '/planets/' + planetName + '/' + postPk + '/comments/',
    type: 'POST',
    dataType: 'json',
    data: {
      csrfmiddlewaretoken: csrftoken,
    },
    success: function (data) {
      for (var i = 0; i < data.length; i++) {
        var comment = data[i];
        if (comment === null) {
          $(window).off('scroll');
          return;
        }

        createcommentContainer(
          comment.profile_image_url,
          comment.nickname,
          comment.created_time,
          comment.content,
          comment.pk,
          comment.user,
          comment.recomments,
          comment.comment_emote_heart,
          comment.comment_emote_thumbsup,
          comment.comment_emote_thumbsdown
        );
      }
    },
  });
}

// 스크롤 첫번째 실행
$(document).ready(function () {
  loadComments();
});

// 댓글 생성 container

function createcommentContainer(
  profile_image_url,
  nickname,
  created_time,
  content,
  comment_pk,
  user,
  recomments,
  comment_emote_heart,
  comment_emote_thumbsup,
  comment_emote_thumbsdown
) {
  var newCommentContainer = document
    .getElementById('container')
    .cloneNode(true);
  var commentSection = newCommentContainer.querySelector('#section');

  if (newCommentContainer.querySelector('#post-votetopics') !== null) {
    newCommentContainer.querySelector('#post-votetopics').remove();
  }
  commentSection.style.display = 'flex';
  var newDiv = document.createElement('div');
  newDiv.innerHTML = `<svg width="30px" height="30px" id="Capa_1" style="enable-background:new 0 0 74.5 60;" version="1.1" viewBox="0 0 74.5 60" width="74.5px" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g><path d="M10,45h40.5v15l24-22l-24-22v15H14V0H0v35C0,40.523,4.477,45,10,45z" fill="#ffffff"/></g></svg>`;
  newCommentContainer.classList = 'bg-[#282c37]';
  commentSection.insertBefore(newDiv, commentSection.children[0]);
  newCommentContainer.querySelector('#comment-create-form').id =
    'recomment-create-form';
  newCommentContainer
    .querySelector('#recomment-create-form')
    .setAttribute('data-comment-pk', comment_pk);
  newCommentContainer.querySelector('#create-button').textContent =
    '대댓글 작성';
  var textarea = newCommentContainer.querySelector('textarea[name="content"]');
  textarea.value = '';
  newCommentContainer.querySelector('#post-img img').src = profile_image_url
    ? profile_image_url
    : '/static/img/no_profile_img.png';
  newCommentContainer.querySelector('#post-nickname').textContent = nickname;
  newCommentContainer.querySelector('#post-nickname').href =
    '/planets/' + planetName + '/profile/' + nickname + '/';
  newCommentContainer.querySelector('#post-createdtime p').textContent =
    created_time;
  newCommentContainer.querySelector('#post-content').textContent = content;
  newCommentContainer.querySelector('#post-tags').remove();
  newCommentContainer.querySelector('#post-image').remove();

  newCommentContainer.querySelector('#update-post-form').id =
    'update-comment-form';
  newCommentContainer
    .querySelector('#update-comment-form')
    .setAttribute('data-comment-pk', comment_pk);
  newCommentContainer.querySelector('#report-post-url').id =
    'report-comment-url';
  newCommentContainer.querySelector('#report-comment-url').textContent =
    '댓글 신고';
  newCommentContainer.querySelector(
    '#report-comment-url'
  ).href = `/planets/${planetName}/report/comment/${comment_pk}/`;
  newCommentContainer.querySelector('#delete-post-form').id =
    'delete-comment-form';
  newCommentContainer
    .querySelector('#delete-comment-form')
    .setAttribute('data-comment-pk', comment_pk);

  newCommentContainer.querySelectorAll('.post-emote-form').forEach((form) => {
    form.setAttribute('data-comment-pk', comment_pk);
  });
  newCommentContainer.querySelector('.emotion-heart-count').textContent =
    comment_emote_heart;
  newCommentContainer.querySelector('.emotion-thumbsup-count').textContent =
    comment_emote_thumbsup;
  newCommentContainer.querySelector('.emotion-thumbsdown-count').textContent =
    comment_emote_thumbsdown;
  newCommentContainer.querySelectorAll('.post-emote-form').forEach((form) => {
    form.classList.replace('post-emote-form', 'comment-emote-form');
    form.id = `comment-emote-form-${comment_pk}`;
  });

  if (requestuser_nickname == nickname) {
    newCommentContainer.querySelector('#dropdown-delete').style.display =
      'block';
    newCommentContainer.querySelector('#delete-post-button').id =
      'delete-comment-button';
    newCommentContainer.querySelector('#delete-comment-button').textContent =
      '댓글 삭제';
    newCommentContainer.querySelector('#update-post-button').id =
      'update-comment-button';
    newCommentContainer.querySelector('#update-comment-button').textContent =
      '댓글 수정';
  } else {
    newCommentContainer.querySelector('#dropdown-delete').remove();
    newCommentContainer
      .querySelector('#update-post-button')
      .closest('li')
      .remove();
  }
  newCommentContainer.querySelector('#comment_form').id = 'recomment_form';
  document.getElementById('comment-list').append(newCommentContainer);
  // newCommentContainer.querySelector('#post-votetopics').remove();

  // 대댓글 있을 경우
  if (recomments) {
    for (var recomment of recomments) {
      var formContainer = document.createElement('div');
      formContainer.id = 'container';
      var newRecommentContainer = createRecommentContainer(
        recomment.profile_image_url,
        recomment.nickname,
        recomment.created_time,
        recomment.content,
        recomment.pk,
        comment_pk
      );
      formContainer.append(newRecommentContainer);
      newCommentContainer.append(formContainer);
    }
  }

  return newCommentContainer;
}

// 대댓글 생성 container
function createRecommentContainer(
  profile_image_url,
  nickname,
  created_time,
  content,
  recomment_pk,
  comment_pk
) {
  var newRecommentContainer = document
    .getElementById('section')
    .cloneNode(true);
  var newDropdownMenu = document
    .getElementById('dropdown-menu')
    .cloneNode(true);

  newRecommentContainer.style.display = 'flex';

  if (newRecommentContainer.querySelector('#post-votetopics') !== null) {
    newRecommentContainer.querySelector('#post-votetopics').remove();
  }
  var newDiv = document.createElement('div');
  newDiv.innerHTML = `<svg width="30px" height="30px" id="Capa_1" style="enable-background:new 0 0 74.5 60;" version="1.1" viewBox="0 0 74.5 60" width="74.5px" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g><path d="M10,45h40.5v15l24-22l-24-22v15H14V0H0v35C0,40.523,4.477,45,10,45z" fill="#ffffff"/></g></svg>`;
  newRecommentContainer.insertBefore(newDiv, newRecommentContainer.children[0]);
  var newDiv2 = document.createElement('div');

  newDiv2.style.width = '50px';
  // newDiv2.style.height = '50px';
  newRecommentContainer.insertBefore(
    newDiv2,
    newRecommentContainer.children[0]
  );
  newRecommentContainer.querySelector('#post-img img').src = profile_image_url
    ? profile_image_url
    : '/static/img/no_profile_img.png';

  newRecommentContainer.querySelector('#post-nickname').textContent = nickname;
  newRecommentContainer.querySelector('#post-nickname').href =
    '/planets/' + planetName + '/profile/' + nickname + '/';
  newRecommentContainer.querySelector('#post-createdtime p').textContent =
    created_time;
  newRecommentContainer.querySelector('#post-content').textContent = content;
  newRecommentContainer.querySelector('#post-tags').remove();
  newRecommentContainer.querySelector('#post-image').remove();
  newRecommentContainer.querySelector('#update-post-form').id =
    'update-recomment-form';
  newRecommentContainer
    .querySelector('#update-recomment-form')
    .setAttribute('data-comment-pk', comment_pk);
  newRecommentContainer
    .querySelector('#update-recomment-form')
    .setAttribute('data-recomment-pk', recomment_pk);
  newRecommentContainer.querySelector('#report-post-url').id =
    'report-recomment-url';
  newRecommentContainer.querySelector('#report-recomment-url').textContent =
    '대댓글 신고';
  newRecommentContainer.querySelector(
    '#report-recomment-url'
  ).href = `/planets/${planetName}/report/recomment/${recomment_pk}/`;
  newRecommentContainer.querySelector('#delete-post-form').id =
    'delete-recomment-form';
  newRecommentContainer
    .querySelector('#delete-recomment-form')
    .setAttribute('data-comment-pk', comment_pk);
  newRecommentContainer
    .querySelector('#delete-recomment-form')
    .setAttribute('data-recomment-pk', recomment_pk);
  if (requestuser_nickname == nickname) {
    newRecommentContainer.querySelector('#dropdown-delete').style.display =
      'block';
    newRecommentContainer.querySelector('#delete-post-button').id =
      'delete-recomment-button';
    newRecommentContainer.querySelector(
      '#delete-recomment-button'
    ).textContent = '대댓글 삭제';
    newRecommentContainer.querySelector('#update-post-button').id =
      'update-recomment-button';
    newRecommentContainer.querySelector(
      '#update-recomment-button'
    ).textContent = '대댓글 수정';
  } else {
    newRecommentContainer.querySelector('#dropdown-delete').remove();
    newRecommentContainer
      .querySelector('#update-post-button')
      .closest('li')
      .remove();
  }
  // newRecommentContainer.querySelector('#post-votetopics').remove();
  var svgDiv = newRecommentContainer
    .querySelector('#comment_form')
    .closest('p')
    .closest('div');
  var newp = document.createElement('p');
  newp.classList.add('w-1/2');
  svgDiv.insertBefore(newp, svgDiv.firstChild);
  var newp2 = document.createElement('p');
  newp2.classList.add('w-1/2');
  svgDiv.insertBefore(newp2, svgDiv.firstChild);
  var newp3 = document.createElement('p');
  newp3.classList.add('w-1/2');
  svgDiv.insertBefore(newp3, svgDiv.firstChild);
  Array.from(
    newRecommentContainer.querySelectorAll('.post-emote-form')
  ).forEach((element) => element.remove());
  newRecommentContainer.querySelector('#comment_form').remove();
  newRecommentContainer.append(newDropdownMenu);

  return newRecommentContainer;
}

// eventlistener
document.addEventListener('DOMContentLoaded', function () {
  document.querySelector('body').addEventListener('click', function (e) {
    var target = e.target;

    // 댓글, 대댓글 작성 svg 클릭
    if (target.tagName == 'svg' && target.id == 'comment_form') {
      var commentForm = document.querySelector('#comment-create-form');

      if (commentForm.style.display == 'none') {
        commentForm.style.display = 'block';
      } else {
        commentForm.style.display = 'none';
      }
    } else if (target.tagName == 'svg' && target.id == 'recomment_form') {
      var parentDiv = target.closest('#container');
      var recommentForm = parentDiv.querySelector('#recomment-create-form');

      if (recommentForm.style.display == 'none') {
        recommentForm.style.display = 'block';
      } else {
        recommentForm.style.display = 'none';
      }
    }
  });

  document.querySelector('body').addEventListener('submit', function (e) {
    var target = e.target;

    // 댓글 생성
    if (target.matches('#comment-create-form')) {
      e.preventDefault();

      var form = target;
      form.style.display = 'none';
      var planetName = form.dataset.planetName;
      var postPk = form.dataset.postPk;
      var url = '/planets/' + planetName + '/' + postPk + '/create/';

      axios({
        url: url,
        method: 'POST',
        data: new FormData(form),
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            var commentList = document.querySelector('#comment-list');
            var newCommentContainer = createcommentContainer(
              response.data.profile_image_url,
              response.data.nickname,
              response.data.created_time,
              response.data.content,
              response.data.comment_pk,
              response.data.user, 
              0,
              0,
              0,
              0
            );
            commentList.append(newCommentContainer);
            form.reset();
          } else {
            console.error(response.data.message);
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 댓글 삭제
    else if (target.matches('#delete-comment-form')) {
      e.preventDefault();

      var deleteButton = target.querySelector('#delete-comment-button');
      var commentContainer = deleteButton.closest('#container');
      var planetName = target.dataset.planetName;
      var commentPk = target.dataset.commentPk;
      var url = '/planets/' + planetName + '/comment/' + commentPk + '/delete/';

      axios({
        url: url,
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success == 'Change') {
            var commentContent =
              commentContainer.querySelector('#post-content');
            commentContent.innerHTML = response.data.comment_content;
          } else if (response.data.success) {
            commentContainer.remove();
          } else {
            console.error('Comment deletion failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 대댓글 생성
    else if (target.matches('#recomment-create-form')) {
      e.preventDefault();

      var form = target;
      form.style.display = 'none';
      var recommentContainer = form.closest('#container');
      var planetName = form.dataset.planetName;
      var postPk = form.dataset.postPk;
      var commentPk = form.dataset.commentPk;

      axios({
        url:
          '/planets/' +
          planetName +
          '/' +
          postPk +
          '/' +
          commentPk +
          '/create/',
        method: 'POST',
        data: new FormData(form),
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            var formContainer = document.createElement('div');
            formContainer.id = 'container';
            formContainer.append(
              createRecommentContainer(
                response.data.profile_image_url,
                response.data.nickname,
                response.data.created_time,
                response.data.content,
                response.data.recomment_pk,
                commentPk
              )
            );
            recommentContainer.append(formContainer);
            form.reset();
          } else {
            console.error(response.data.message);
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 대댓글 삭제
    else if (target.matches('#delete-recomment-form')) {
      e.preventDefault();

      var deleteButton = target.querySelector('#delete-recomment-button');
      var recommentContainer = deleteButton.closest('#container');
      var planetName = target.dataset.planetName;
      var postPk = target.dataset.postPk;
      var commentPk = target.dataset.commentPk;
      var recommentPk = target.dataset.recommentPk;
      var url =
        '/planets/' + planetName + '/recomment/' + recommentPk + '/delete/';

      axios({
        url: url,
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            recommentContainer.remove();
          } else {
            console.error('Recomment deletion failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 댓글 수정 form
    else if (target.matches('#update-comment-form')) {
      e.preventDefault();

      var updateForm = target;
      var updateButton = updateForm.querySelector('#update-comment-button');
      var postContainer = updateButton.closest('#container');
      var planetName = updateForm.dataset.planetName;
      var postPk = updateForm.dataset.postPk;
      var commentPk = updateForm.dataset.commentPk;
      var formData = new FormData(updateForm);

      axios({
        url:
          '/planets/' +
          planetName +
          '/' +
          postPk +
          '/' +
          commentPk +
          '/update/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            var formHtml = response.data.form_html;
            var formContainer = document.createElement('div');
            formContainer.innerHTML = formHtml;
            formContainer.querySelector('label[for="id_content"]').innerHTML =
              '<p class="text-base text-white">내용</p>';
            var formElement = document.createElement('form');
            formElement.id = 'edit-comment-form';
            formElement.setAttribute('data-planet-name', planetName);
            formElement.setAttribute('data-post-pk', postPk);
            formElement.setAttribute('data-comment-pk', commentPk);
            formElement.appendChild(formContainer);
            var submitButton = document.createElement('button');
            submitButton.id = 'edit-comment-button';
            submitButton.classList.add(
              'chatting-create-btn',
              'bg-[#bcbdbf]',
              'mx-auto'
            );
            submitButton.textContent = '댓글 수정';
            submitButton.type = 'submit';
            formContainer.append(submitButton);
            postContainer.querySelector('#section').style.display = 'none';
            postContainer.insertBefore(formElement, postContainer.children[0]);
          } else {
            console.error('Comment deletion failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 댓글 수정 처리
    else if (target.matches('#edit-comment-form')) {
      e.preventDefault();

      var editForm = target;
      var editButton = editForm.querySelector('#edit-comment-button');
      var postContainer = editButton.closest('#container');
      var planetName = editForm.dataset.planetName;
      var postPk = editForm.dataset.postPk;
      var commentPk = editForm.dataset.commentPk;
      var formData = new FormData(editForm);

      axios({
        url:
          '/planets/' +
          planetName +
          '/' +
          postPk +
          '/' +
          commentPk +
          '/update/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            postContainer.querySelector('#section').style.display = 'flex';
            postContainer.querySelector('#post-content').textContent =
              response.data.content;
            if (response.data.user == requestuser) {
              postContainer.querySelector('#dropdown-delete').style.display =
                'block';
            }
            postContainer.querySelector('#edit-comment-form').remove();
            editForm.reset();
          } else {
            // var divIdContent = editForm.querySelector("#div_id_content");
            // var newP = document.createElement("p");
            // newP.id = "error_1_id_content";
            // newP.className = "text-red-500 text-xs italic";
            // var strongElement = document.createElement("strong");
            // strongElement.textContent = JSON.parse(response.data.errors).content[0].message;
            // newP.appendChild(strongElement);
            // divIdContent.appendChild(newP);
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 대댓글 수정 form
    else if (target.matches('#update-recomment-form')) {
      e.preventDefault();

      var updateForm = target;
      var updateButton = updateForm.querySelector('#update-recomment-button');
      var postContainer = updateButton.closest('#container');
      var postSection = updateButton.closest('#section');
      var planetName = updateForm.dataset.planetName;
      var postPk = updateForm.dataset.postPk;
      var commentPk = updateForm.dataset.commentPk;
      var recommentPk = updateForm.dataset.recommentPk;
      var formData = new FormData(updateForm);

      axios({
        url:
          '/planets/' +
          planetName +
          '/' +
          postPk +
          '/' +
          commentPk +
          '/' +
          recommentPk +
          '/update/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            var formHtml = response.data.form_html;
            var formContainer = document.createElement('div');
            formContainer.innerHTML = formHtml;
            formContainer.querySelector('label[for="id_content"]').innerHTML =
              '<p class="text-base text-white">내용</p>';
            var formElement = document.createElement('form');
            formElement.id = 'edit-recomment-form';
            formElement.setAttribute('data-planet-name', planetName);
            formElement.setAttribute('data-post-pk', postPk);
            formElement.setAttribute('data-comment-pk', commentPk);
            formElement.setAttribute('data-recomment-pk', recommentPk);
            formElement.appendChild(formContainer);
            var submitButton = document.createElement('button');
            submitButton.id = 'edit-recomment-button';
            submitButton.classList.add(
              'chatting-create-btn',
              'bg-[#bcbdbf]',
              'mx-auto'
            );
            submitButton.textContent = '대댓글 수정';
            submitButton.type = 'submit';
            formContainer.append(submitButton);
            postSection.style.display = 'none';
            postContainer.insertBefore(formElement, postContainer.children[1]);
          } else {
            console.error('Comment deletion failed.');
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }

    // 대댓글 수정 처리
    else if (target.matches('#edit-recomment-form')) {
      e.preventDefault();

      var editForm = target;
      var editButton = editForm.querySelector('#edit-recomment-button');
      var postContainer = editButton.closest('#container');
      var planetName = editForm.dataset.planetName;
      var postPk = editForm.dataset.postPk;
      var commentPk = editForm.dataset.commentPk;
      var recommentPk = editForm.dataset.recommentPk;
      var formData = new FormData(editForm);

      axios({
        url:
          '/planets/' +
          planetName +
          '/' +
          postPk +
          '/' +
          commentPk +
          '/' +
          recommentPk +
          '/update/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      })
        .then(function (response) {
          if (response.data.success) {
            postContainer.querySelector('#section').style.display = 'flex';
            postContainer.querySelector('#post-content').textContent =
              response.data.content;
            if (response.data.user == requestuser) {
              postContainer.querySelector('#dropdown-delete').style.display =
                'block';
            }
            postContainer.querySelector('#edit-recomment-form').remove();
            editForm.reset();
          } else {
            // var divIdContent = editForm.querySelector("#div_id_content");
            // var newP = document.createElement("p");
            // newP.id = "error_1_id_content";
            // newP.className = "text-red-500 text-xs italic";
            // var strongElement = document.createElement("strong");
            // strongElement.textContent = JSON.parse(response.data.errors).content[0].message;
            // newP.appendChild(strongElement);
            // divIdContent.appendChild(newP);
          }
        })
        .catch(function (error) {
          console.error('AJAX request failed:', error);
        });
    }
  });
});

// comment 비동기 emote
document.addEventListener('DOMContentLoaded', function () {
  document.querySelector('body').addEventListener('submit', (e) => {
    if (e.target.matches('.comment-emote-form')) {
      e.preventDefault();
      const emoteClass = e.target.dataset.emoteClass;
      const planetName = e.target.dataset.planetName;
      const postPk = e.target.dataset.postPk;
      const commentPk = e.target.dataset.commentPk;
      const emotionCount = document.querySelector(
        `#comment-emote-form-${commentPk}> p > .emotion-${emoteClass}-count`
      );
      axios({
        method: 'post',
        url: `/planets/${planetName}/posts/${postPk}/comments/${commentPk}/emotes/${emoteClass}`,
        headers: { 'X-CSRFToken': csrftoken },
      })
        .then((response) => {
          emotionCount.innerHTML = response.data.emotion_count;
        })
        .catch((error) => {
          console.log(error.response);
        });
    }
  });
});
