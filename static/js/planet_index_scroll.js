var planetName = document
  .getElementById('post-form')
  .getAttribute('data-planet-name');
var page = 1;
var isLoading = false; // 로딩 중인지 여부를 나타내는 변수

// 스크롤 이벤트와 터치 이벤트 모두 처리
$(window).on('scroll touchmove', function () {
  if (
    !isLoading &&
    $(window).scrollTop() + $(window).height() >= $(document).height() - 100
  ) {
    page++;
    loadPosts(page);
  }
});


// posts rendering 비동기 처리
function loadPosts(page) {
  isLoading = true; // 로딩 중 상태로 설정

  $.ajax({
    url: '/planets/' + planetName + '/posts/',
    type: 'POST',
    data: {
      page: page,
      csrfmiddlewaretoken: csrftoken,
    },
    dataType: 'json',

    success: function (data) {
      for (var i = 0; i < data.length; i++) {
        var post = data[i];

        if (post === null) {
          $(window).off('scroll touchmove');
          return;
        }

        $('#post-list').append(
          createpostContainer(
            post.profile_image_url,
            post.nickname,
            post.created_time,
            post.content,
            post.tags,
            post.pk,
            post.image_url,
            post.user,
            post.votetopics,
            post.post_emote_heart,
            post.post_emote_thumbsup,
            post.post_emote_thumbsdown,
            post.vote_count,
            post.voted
          )
        );
      }
    },
    complete: function () {
      isLoading = false; // 로딩 완료 상태로 설정
    },
  });
}

// 스크롤 이벤트 첫번째 실행
$(document).ready(function () {
  loadPosts(page);
});
