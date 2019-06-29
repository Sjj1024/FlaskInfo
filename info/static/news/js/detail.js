function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    })

    // 收藏
    $(".collection").click(function () {

        var params = {
            "news_id": $(this).attr('data-newid'),
            "action": "collect"
        }
        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 收藏成功
                    // 隐藏收藏按钮
                    $(".collection").hide();
                    // 显示取消收藏按钮
                    $(".collected").show();
                }else if (resp.errno == "4101"){
                    $('.login_form_con').show();
                }else{
                    alert(resp.errmsg);
                }
            }
        })

    })

    // 取消收藏
    $(".collected").click(function () {
        var params = {
            "news_id": $(this).attr('data-newid'),
            "action": "cancel_collect"
        }
        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 收藏成功
                    // 隐藏收藏按钮
                    $(".collection").show();
                    // 显示取消收藏按钮
                    $(".collected").hide();
                }else if (resp.errno == "4101"){
                    $('.login_form_con').show();
                }else{
                    alert(resp.errmsg);
                }
            }
        })

    })

    // 评论提交
     $(".comment_form").submit(function (e) {
        e.preventDefault();
        var news_id = $(this).attr('data-newsid')
        var news_comment = $(".comment_input").val();

        if (!news_comment) {
            alert('请输入评论内容');
            return
        }
        var params = {
            "news_id": news_id,
            "comment": news_comment
        };
        $.ajax({
            url: "/news/news_comment",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == '0') {
                    var comment = resp.data
                    // 拼接内容
                    var comment_html = ''
                    comment_html += '<div class="comment_list">'
                    comment_html += '<div class="person_pic fl">'
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    }else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>'
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>'
                    comment_html += '<div class="comment_text fl">'
                    comment_html += comment.content
                    comment_html += '</div>'
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>'

                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>'
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                    comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + news_id + '">'
                    comment_html += '<textarea class="reply_input"></textarea>'
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">'
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                    comment_html += '</form>'

                    comment_html += '</div>'
                    // 拼接到内容的前面
                    $(".comment_list_con").prepend(comment_html)
                    // 让comment_sub 失去焦点
                    $('.comment_sub').blur();
                    // 清空输入框内容
                    $(".comment_input").val("")
                    // 刷新评论条数
                    updateCommentCount()
                }else {
                    alert(resp.errmsg)
                }
            }
        })

    })
    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            // 设置默认的点赞还是取消点赞的操作【默认是点赞】
            var action = "add"
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                action = "remove"
            }

            var comment_id = $(this).attr("data-commentid")
            var params = {
                "comment_id": comment_id,
                "action": action,
            }

            $.ajax({
                url: "/news/comment_like",
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    if (resp.errno == "0") {
                        // 更新点赞按钮图标
                        var like_count = $this.attr('data-likecount')
                        // 更新点赞按钮图标
                        if (action == "add") {
                            like_count = parseInt(like_count) + 1
                            // 代表是点赞
                            $this.addClass('has_comment_up')
                        }else {
                            like_count = parseInt(like_count) - 1
                            $this.removeClass('has_comment_up')
                        }
                        // 更新点赞数据
                        $this.attr('data-likecount', like_count)
                        if (like_count == 0) {
                            $this.html("赞")
                        }else {
                            $this.html(like_count)
                        }
                    }else if (resp.errno == "4101"){
                        $('.login_form_con').show();
                    }else {
                        alert(resp.errmsg)
                    }
                }
            })
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            alert('回复评论')
        }
    })

        // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})


// 更新评论条数
function updateCommentCount() {
    var count = $(".comment_list").length
    $(".comment_count").html(count+"条评论")
}