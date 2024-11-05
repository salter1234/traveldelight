$(document).ready(function() {
    // 确保 CSRF Token 在 AJAX 请求中被包含
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

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
                // 刷新页面
                location.reload(); 
            },
            error: function(xhr, errmsg, err) {
                $('#message').html('<div class="alert alert-danger" role="alert">更新失败，请稍后重试。</div>');
            }
        });
    });
});