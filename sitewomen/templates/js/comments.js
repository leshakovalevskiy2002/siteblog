const commentForm = document.forms.commentForm;
const commentFormContent = commentForm.body;
const commentFormParentInput = commentForm.parent;
const commentFormSubmit = commentForm.commentSubmit;
const commentPostSlug = commentForm.getAttribute('data-post-slug');
const langPrefix = "/" + commentForm.getAttribute('data-lang');

commentForm.addEventListener('submit', createComment);
replyUser()

function replyUser() {
  document.querySelectorAll('.btn-reply').forEach(e => {
    e.addEventListener('click', replyComment);
  });
}

function replyComment() {
  const commentUsername = this.getAttribute('data-comment-username');
  const commentMessageId = this.getAttribute('data-comment-id');
  commentFormContent.value = `${commentUsername}, `;
  commentFormParentInput.value = commentMessageId;
}

async function createComment(event) {
    event.preventDefault();
    commentFormSubmit.disabled = true;
    commentFormSubmit.innerText = "Ожидаем ответа сервера";
    try {
        const response = await fetch(`${langPrefix}/post/${commentPostSlug}/comments/create/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: new FormData(commentForm),
        });
        const comment = await response.json();
        console.log(`${comment.lang}`);
        console.log(`${comment.translations}`);
        console.log(`${comment.translations.updated}`);
        let commentTemplate = `<ul id="comment-thread-${comment.id}">
                                    <li class="card border-0">
                                        <div>
                                            <img class="rounded-circle" width="50" src="${comment.avatar}">
                                            <p class="m-0 text-dark d-inline-block">
                                                <span class="fw-bold"><a class="text-decoration-none" href="${comment.get_absolute_url}">
                                                ${comment.author}</a></span>
                                                <span class="text-secondary">${comment.updated_text}</span>
                                            </p>
                                            <div class="mb-1" style="max-height: 200px; overflow-y: auto; word-break: break-all;">
                                            `;

        if (comment.parent_id !== null) {
            commentTemplate += `<span class="fw-bold">${comment.parent_comment_author}</span>, `;
        }

        commentTemplate += `${comment.content}
                            </div>
                            `;

        if (comment.is_updated) {
            commentTemplate += `<p class="text-secondary fw-light fst-italic">${comment.translations.updated} ${comment.updated_text}</p>
            `;
        }

        commentTemplate += `<a class="btn btn-light text-decoration-none btn-reply" href="#commentForm" data-comment-id="${comment.id}"
     data-comment-username="${comment.author}">
      <img width="20" src="/static/women/images/reply.png" alt="${comment.translations.reply}"> ${comment.translations.reply}
  </a>`;

        if (comment.request_user === comment.author) {
            commentTemplate += ` <a class="btn btn-light text-decoration-none text-dark" href="${comment.comment_url}">
                        <img width="20" src="/static/women/images/edit.png" alt="${comment.translations.edit}">
                        ${comment.translations.edit}</a>`;
        }

        commentTemplate += `</div></li></ul>`;

        if (comment.is_child) {
            document.querySelector(`#comment-thread-${comment.parent_id}`).insertAdjacentHTML("beforeend", commentTemplate);
        }
        else {
            const noCommentsElement = document.querySelector('#delete-text');
            if (noCommentsElement) {
                const newContainer = document.createElement('div');
                newContainer.className = 'nested-comments';
                newContainer.innerHTML = commentTemplate;
                noCommentsElement.replaceWith(newContainer);
            }
            else {
                document.querySelector('.nested-comments').insertAdjacentHTML("beforeend", commentTemplate);
            }

            const CountCommentsElement = document.querySelector('#count-comments');
            const newContainer = document.createElement('h2');
            newContainer.id = 'count-comments';
            newContainer.innerHTML = `${comment.count_comments_text}`;
            CountCommentsElement.replaceWith(newContainer);

            console.log(CountCommentsElement);
        }
        commentForm.reset()
        commentFormSubmit.disabled = false;
        commentFormSubmit.innerText = "Добавить комментарий";
        commentFormParentInput.value = null;
        replyUser();
    }
    catch (error) {
        console.log(error)
    }
}