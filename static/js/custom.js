$(document).ready(function() {
    // jQuery AJAX 提交表单
    $('#profile-edit-form').submit(function(e) {
      e.preventDefault(); // 防止默认表单提交
  
      var formData = new FormData(this); // 获取表单数据
  
      $.ajax({
        url: "{% url 'profile_edit' %}", // 表单提交的 URL
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          $('#message').html('<div class="alert alert-success" role="alert">资料更新成功！</div>');
          $('.alert-success').fadeOut(3000);  // 3 秒后淡出
        },
        error: function(xhr, errmsg, err) {
          $('#message').html('<div class="alert alert-danger" role="alert">更新失败，请稍后重试。</div>');
        }
      });
    });
  });