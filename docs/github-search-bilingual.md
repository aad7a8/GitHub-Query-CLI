# GitHub Search 100 個真實搜尋對照表（中英對照版）

> **資料來源**：100% 取自 GitHub 官方文件 (`docs.github.com`) 與 freeCodeCamp 教學文章上的真實範例。「英文敘述」欄位即為官方原文，「中文敘述」為其翻譯。
>
> **來源頁面**：
>
> - [Searching for repositories](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
> - [Searching issues and pull requests](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests)
> - [Searching users](https://docs.github.com/en/search-github/searching-on-github/searching-users)
> - [GitHub Search Tips (freeCodeCamp)](https://www.freecodecamp.org/news/github-search-tips/)
> - [Good First Issue Guide (github-help-wanted.com)](https://github-help-wanted.com/open-source/good-first-issue/)
>
> **使用方式**：複製右欄的「搜尋字串」貼到 GitHub 搜尋框（按 `/` 喚出）。

---

## A 組｜搜 Repositories（找專案）


| #   | 我想找什麼（中文）                                             | I'm looking for... (English, official wording)                                                            | 搜尋字串                                 |
| --- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | 找名字裡有 "jquery" 的 repo。                                | Repositories with "jquery" in the repository name.                                                        | `jquery in:name`                     |
| 2   | 找 repo 名稱**或描述**裡含 "jquery" 的。                        | Repositories with "jquery" in the repository name or description.                                         | `jquery in:name,description`         |
| 3   | 找被打上 "jquery" 主題標籤的 repo。                             | Repositories labeled with "jquery" as a topic.                                                            | `jquery in:topics`                   |
| 4   | 找 README 檔案裡提到 "jquery" 的 repo。                       | Repositories mentioning "jquery" in the repository's README file.                                         | `jquery in:readme`                   |
| 5   | 直接定位某個特定 repo。                                        | Match a specific repository name.                                                                         | `repo:octocat/hello-world`           |
| 6   | 找 @defunkt 這個人擁有、且被 fork 超過 100 次的 repo。              | Repositories from @defunkt that have more than 100 forks.                                                 | `user:defunkt forks:>100`            |
| 7   | 找 GitHub 這個組織底下所有 repo。                               | Repositories from GitHub.                                                                                 | `org:github`                         |
| 8   | 找剛好 1 MB 大小的 repo。                                    | Repositories that are 1 MB exactly.                                                                       | `size:1000`                          |
| 9   | 找至少 30 MB 大的 repo。                                    | Repositories that are at least 30 MB.                                                                     | `size:>=30000`                       |
| 10  | 找小於 50 KB 的 repo。                                     | Repositories that are smaller than 50 KB.                                                                 | `size:<50`                           |
| 11  | 找大小介於 50 KB 到 120 KB 之間的 repo。                        | Repositories that are between 50 KB and 120 KB.                                                           | `size:50..120`                       |
| 12  | 找有 1 萬以上追蹤者、且提到 "node" 的 repo。                        | Repositories with 10,000 or more followers mentioning the word "node".                                    | `node followers:>=10000`             |
| 13  | 找追蹤者 1–10 人、提到 "styleguide linter" 的 repo。            | Repositories with between 1 and 10 followers, mentioning the word "styleguide linter."                    | `styleguide linter followers:1..10`  |
| 14  | 找剛好 5 個 fork 的 repo。                                  | Repositories with only five forks.                                                                        | `forks:5`                            |
| 15  | 找 fork 數至少 205 的 repo。                                | Repositories with at least 205 forks.                                                                     | `forks:>=205`                        |
| 16  | 找 fork 數少於 90 的 repo。                                 | Repositories with fewer than 90 forks.                                                                    | `forks:<90`                          |
| 17  | 找 fork 數介於 10–20 之間的 repo。                            | Repositories with 10 to 20 forks.                                                                         | `forks:10..20`                       |
| 18  | 找剛好 500 顆星的 repo。                                     | Repositories with exactly 500 stars.                                                                      | `stars:500`                          |
| 19  | 找 10–20 顆星、而且小於 1000 KB 的 repo。                       | Repositories with 10 to 20 stars, that are smaller than 1000 KB.                                          | `stars:10..20 size:<1000`            |
| 20  | 找至少 500 顆星、PHP 寫的 repo（包含 fork）。                      | Repositories with at least 500 stars, including forked ones, that are written in PHP.                     | `stars:>=500 fork:true language:php` |
| 21  | 找 2011 年前建立、含 "webos" 的 repo。                         | Repositories with the word "webos" that were created before 2011.                                         | `webos created:<2011-01-01`          |
| 22  | 找含 "css"、且 2013 年 2 月後還有 push 的 repo。                 | Repositories with the word "css" that were pushed to after January 2013.                                  | `css pushed:>2013-02-01`             |
| 23  | 找 JavaScript 寫的、含 "rails" 的 repo。                     | Repositories with the word "rails" that are written in JavaScript.                                        | `rails language:javascript`          |
| 24  | 找被打上 "jekyll" 主題標籤的所有 repo。                           | Repositories that have been classified with the topic "Jekyll."                                           | `topic:jekyll`                       |
| 25  | 找有正好 5 個主題標籤的 repo。                                   | Repositories that have five topics.                                                                       | `topics:5`                           |
| 26  | 找有超過 3 個主題標籤的 repo。                                   | Repositories that have more than three topics.                                                            | `topics:>3`                          |
| 27  | 找用 Apache License 2.0 授權的 repo。                       | Repositories that are licensed under Apache License 2.0.                                                  | `license:apache-2.0`                 |
| 28  | 找 GitHub 公司名下所有公開 repo。                               | Public repositories owned by GitHub.                                                                      | `is:public org:github`               |
| 29  | 找你能存取、含 "pages" 的私有 repo。                             | Private repositories that you can access and contain the word "pages."                                    | `is:private pages`                   |
| 30  | 找已封存（停止維護）、含 "GNOME" 的 repo。                          | Repositories that are archived and contain the word "GNOME."                                              | `archived:true GNOME`                |
| 31  | 找**未**封存、含 "GNOME" 的 repo。                            | Repositories that are not archived and contain the word "GNOME."                                          | `archived:false GNOME`               |
| 32  | 找有超過 2 個 "good first issue" 標籤、含 "javascript" 的 repo。 | Repositories with more than two issues labeled `good-first-issue` and that contain the word "javascript." | `good-first-issues:>2 javascript`    |
| 33  | 找有超過 4 個 "help wanted" 標籤、含 "react" 的 repo。           | Repositories with more than four issues labeled `help-wanted` and that contain the word "React."          | `help-wanted-issues:>4 react`        |
| 34  | 找作者可以被 GitHub Sponsors 贊助的 repo。                      | Repositories whose owners have a GitHub Sponsors profile.                                                 | `is:sponsorable`                     |


---

## B 組｜搜 Issues / Pull Requests（追蹤工作 / 找貢獻機會）


| #   | 我想找什麼（中文）                                      | I'm looking for... (English, official wording)                                                     | 搜尋字串                                             |
| --- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| 35  | 找含 "cat" 字眼的 PR。                               | Pull requests with the word "cat."                                                                 | `cat type:pr`                                    |
| 36  | 找含 "github"、而且 @defunkt 有留言過的 issue。           | Issues that contain the word "github," and have a comment by @defunkt.                             | `github commenter:defunkt type:issue`            |
| 37  | 找含有 "warning" 在標題裡的 issue。                     | Issues with "warning" in their title.                                                              | `warning in:title`                               |
| 38  | 找標題或內文含 "error" 的 issue。                       | Issues with "error" in their title or body.                                                        | `error in:title,body`                            |
| 39  | 找留言中提到 "shipit" 的 issue。                       | Issues mentioning "shipit" in their comments.                                                      | `shipit in:comments`                             |
| 40  | 找 @mozilla 的 shumway 專案中、2012 年 3 月前建立的 issue。 | Issues from @mozilla's shumway project that were created before March 2012.                        | `repo:mozilla/shumway created:<2012-03-01`       |
| 41  | 找關閉、標籤是 "bug" 的 issue。                         | Closed issues with the label "bug."                                                                | `is:issue label:bug is:closed`                   |
| 42  | 找含 "libraries"、被以「**已完成**」原因關閉的 issue。         | Issues with the word "libraries" that were closed as "completed."                                  | `libraries is:closed reason:completed`           |
| 43  | 找含 "libraries"、被以「**不打算處理**」原因關閉的 issue。       | Issues with the word "libraries" that were closed as "not planned."                                | `libraries is:closed reason:"not planned"`       |
| 44  | 找 @gjtorikian 寫的、含 "cool" 的 issue 或 PR。        | Issues and pull requests with the word "cool" that were created by @gjtorikian.                    | `cool author:gjtorikian`                         |
| 45  | 找 libgit2/libgit2 專案中、被指派給 @vmg 的 issue/PR。    | Issues and pull requests in libgit2's project libgit2 that are assigned to @vmg.                   | `assignee:vmg repo:libgit2/libgit2`              |
| 46  | 找含 "resque"、提到 @defunkt 的 issue。               | Issues with the word "resque" that mention @defunkt.                                               | `resque mentions:defunkt`                        |
| 47  | 找你自己建立的所有 issue 和 PR。                          | Issues and pull requests you have authored.                                                        | `author:@me`                                     |
| 48  | 找 Ruby 寫的專案中、標籤為 "help wanted" 的 issue。        | Issues with the label "help wanted" that are in Ruby repositories.                                 | `label:"help wanted" language:ruby`              |
| 49  | 找同時帶 "bug" **和** "resolved" 兩個標籤的 issue。       | Issues with the labels "bug" and "resolved."                                                       | `label:bug label:resolved`                       |
| 50  | 找有 "bug" **或** "resolved" 標籤的 issue。           | Issues with the label "bug" or the label "resolved."                                               | `label:bug,resolved`                             |
| 51  | 找關閉、留言超過 100 則的 issue。                         | Closed issues with more than 100 comments.                                                         | `state:closed comments:>100`                     |
| 52  | 找互動數（留言+反應）超過 2000 的 issue/PR。                 | Pull requests or issues with more than 2000 interactions.                                          | `interactions:>2000`                             |
| 53  | 找 reaction 數超過 1000 的 issue。                   | Issues with more than 1000 reactions.                                                              | `reactions:>1000`                                |
| 54  | 找草稿狀態的 PR。                                     | Draft pull requests.                                                                               | `draft:true`                                     |
| 55  | 找已被 reviewer 核可的 PR。                           | Pull requests that a reviewer has approved.                                                        | `type:pr review:approved`                        |
| 56  | 找 @benbalter 被指名 review 的 PR。                  | Pull requests where a specific person is requested for review.                                     | `type:pr review-requested:benbalter`             |
| 57  | 找指名「我」要 review 的 PR。                           | Pull requests that you have directly been asked to review.                                         | `type:pr user-review-requested:@me`              |
| 58  | 找 C# 寫的、2011 年前建立、還沒關的 issue。                  | Open issues that were created before 2011 in repositories written in C#.                           | `language:c# created:<2011-01-01 state:open`     |
| 59  | 找 Swift 寫的、2014/6/11 之後關閉的 issue/PR。           | Issues and pull requests in Swift that were closed after June 11, 2014.                            | `language:swift closed:>2014-06-11`              |
| 60  | 找 JavaScript 寫的、2011 年前合併的 PR。                 | Pull requests in JavaScript repositories that were merged before 2011.                             | `language:javascript merged:<2011-01-01`         |
| 61  | 找含 "bug"、已合併的 PR。                              | Merged pull requests with the word "bug."                                                          | `bug is:pr is:merged`                            |
| 62  | 找從 "change" 開頭分支發出、已關閉但**未合併**的 PR。            | Pull requests opened from branch names beginning with the word "change" that are closed.           | `head:change is:closed is:unmerged`              |
| 63  | 找要合併進 `gh-pages` 分支的 PR。                       | Pull requests that are being merged into the `gh-pages` branch.                                    | `base:gh-pages`                                  |
| 64  | 找含 "priority"、卻**沒有任何標籤**的 issue/PR。           | Issues and pull requests with the word "priority" that also don't have any labels.                 | `priority no:label`                              |
| 65  | 找含 "important"、Java 寫、**沒人被指派**的 issue。        | Issues not associated with an assignee, containing the word "important," and in Java repositories. | `important no:assignee language:java type:issue` |


---

## C 組｜搜 Users（找人 / 獵才 / 追蹤）


| #   | 我想找什麼（中文）                          | I'm looking for... (English, official wording)                                           | 搜尋字串                                         |
| --- | ---------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------- |
| 66  | 找 2011 年前註冊、名字含 "mike" 的個人帳號。      | Personal accounts named "mike" that were created before 2011.                            | `mike in:name created:<2011-01-01 type:user` |
| 67  | 找信箱含 "data" 的組織帳號。                 | Organizations with the word "data" in their email.                                       | `data in:email type:org`                     |
| 68  | 找帳號名為 "octocat" 的使用者。              | The user with the username "octocat".                                                    | `user:octocat`                               |
| 69  | 找登入名稱（username）含 "kenya" 的使用者。     | Users with the word "kenya" in their username.                                           | `kenya in:login`                             |
| 70  | 找真實姓名是 "Nat Friedman" 的人。          | A user with the full name "Nat Friedman."                                                | `fullname:nat friedman`                      |
| 71  | 找擁有超過 9000 個 repo 的使用者。            | Users whose repository count is over 9,000.                                              | `repos:>9000`                                |
| 72  | 找名字含 "bert"、擁有 10–30 個 repo 的人。    | Users with the word "bert" in their username or real name who own 10 to 30 repositories. | `bert repos:10..30`                          |
| 73  | 找住在冰島、只有 1 個 repo 的人。              | Users with exactly one repository that live in Iceland.                                  | `repos:1 location:iceland`                   |
| 74  | 找住在俄羅斯、主力寫 JavaScript 的開發者。        | Users in Russia with a majority of their repositories written in JavaScript.             | `language:javascript location:russia`        |
| 75  | 找 2011 年前加入 GitHub 的老用戶。           | Users that joined before 2011.                                                           | `created:<2011-01-01`                        |
| 76  | 找 2013/3/6 那天加入、地點寫倫敦的人。           | Users that joined on March 6th, 2013, who list their location as London.                 | `created:2013-03-06 location:london`         |
| 77  | 找有 1000 以上 follower 的開發者。          | Users with 1,000 or more followers.                                                      | `followers:>=1000`                           |
| 78  | 找名字含 "sparkle"、follower 在 1–10 的人。 | Users with between 1 and 10 followers, with the word "sparkle" in their name.            | `sparkle followers:1..10`                    |


---

## D 組｜常見實戰組合（freeCodeCamp 教學原文）


| #   | 我想找什麼（中文）                                 | I'm looking for... (English, original wording)                                    | 搜尋字串                                  |
| --- | ----------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------- |
| 79  | 列出全 GitHub 標籤為 "starter" 的開放 issue。       | All open issues from across GitHub that are labeled "starter."                    | `is:issue is:open label:starter`      |
| 80  | 列出標籤為 "up-for-grabs" 的開放 issue。           | Open issues that are ready to be worked on if you have the necessary skills.      | `is:issue is:open label:up-for-grabs` |
| 81  | 列出**沒有被分配到任何 project** 的開放 issue。         | All open issues that are not assigned to a specific project.                      | `no:project type:issue is:open`       |
| 82  | 列出**沒有里程碑（milestone）**的開放 issue。          | Issues that are not tracked with milestones.                                      | `no:milestone type:issue is:open`     |
| 83  | 列出**沒被打任何標籤**的開放 issue。                   | All open issues that are not labeled.                                             | `no:label type:issue is:open`         |
| 84  | 列出**沒人被指派**的開放 issue。                     | All open issues that have not yet been assigned to a person.                      | `is:issue is:open no:assignee`        |
| 85  | 列出 freeCodeCamp 組織底下的所有公開 repo。           | All public repositories owned by freeCodeCamp.                                    | `is:public org:freecodecamp`          |
| 86  | 找 2022/10/1 之後建立、含 "freecodecamp" 的 repo。 | All repositories with the word "freeCodeCamp" that were created after 2022-10-01. | `freecodecamp created:>2022-10-01`    |
| 87  | 找名字含 "Data Science" 的 repo。               | Repositories with "Data Science" in the repository name.                          | `Data Science in:name`                |
| 88  | 找描述裡提到 "freeCodeCamp" 的 repo。             | Repositories where the term "freeCodeCamp" is included in the description.        | `freecodecamp in:description`         |


---

## E 組｜github-help-wanted.com 推薦的真實工作流（找開源貢獻機會）


| #   | 我想找什麼（中文）                                        | I'm looking for... (English, original wording)                              | 搜尋字串                                                            |
| --- | ------------------------------------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------- |
| 89  | 找全 GitHub 開放、標籤為 "good first issue" 的 issue。     | Beginner-friendly labels: open issues with the "good first issue" label.    | `is:issue is:open label:"good first issue"`                     |
| 90  | 找開放、同時帶 "help wanted" 與 "documentation" 的 issue。 | Open issues with both "help wanted" and "documentation" labels.             | `is:issue is:open label:"help wanted" label:"documentation"`    |
| 91  | 找開放、標 "good first issue"、Python 專案的 issue。       | Narrow by language (helps match your skills): "good first issue" in Python. | `is:issue is:open label:"good first issue" language:Python`     |
| 92  | 找開放、標 "good first issue"、JavaScript 專案的 issue。   | Narrow by language: "good first issue" in JavaScript.                       | `is:issue is:open label:"good first issue" language:JavaScript` |
| 93  | 鎖定某個 repo 的 "good first issue"。                  | Narrow to a specific repo (high intent).                                    | `repo:OWNER/REPO is:issue is:open label:"good first issue"`     |
| 94  | 鎖定某個 repo 的 "help wanted" issue。                 | Narrow to a specific repo: "help wanted" issues.                            | `repo:OWNER/REPO is:issue is:open label:"help wanted"`          |


---

## F 組｜其他實戰範例（官方 docs 補充）


| #   | 我想找什麼（中文）                                    | I'm looking for... (English, official wording)                                                                                 | 搜尋字串                                                |
| --- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| 95  | 找含 "android"、已關閉的 issue 和 PR。                | Closed issues and pull requests with the word "android."                                                                       | `android is:closed`                                 |
| 96  | 找標題含 "fast"、Ruby 寫、2014/5 後合併的 PR。           | Pull requests in Ruby with the word "fast" in the title that were merged after May 2014.                                       | `fast in:title language:ruby merged:>=2014-05-01`   |
| 97  | 找 2015/5 月內建立、commit 狀態為失敗的 PR。              | Pull requests opened on May 2015 with a failed status.                                                                         | `created:2015-05-01..2015-05-30 status:failure`     |
| 98  | 找 commit SHA 開頭為 `e1109ab` 的 PR。             | Pull requests with a commit SHA that starts with `e1109ab`.                                                                    | `e1109ab`                                           |
| 99  | 找留言介於 500–1000 則的 issue。                     | Issues with comments ranging from 500 to 1,000.                                                                                | `comments:500..1000`                                |
| 100 | 找含 "code of conduct"、對話被鎖、且 repo 未封存的 issue。 | Issues or pull requests with the words "code of conduct" that have a locked conversation in a repository that is not archived. | `code of conduct is:locked is:issue archived:false` |


---

## 心法內化（五歲小孩版）

GitHub 的搜尋語法就像點飲料：

- 「珍奶」= 模糊版，店員會問你一堆事情。
- 「中杯、半糖、少冰、加椰果、紅茶基底」= 一次到位。

**冒號 `:` 後面接的就是「規格選項」**，每多一個選項，搜尋結果越精準。

---

## 口訣記憶（三個重點）

1. **「`in:` 限縮位置，`is:` 限縮狀態」** — `in:title` 是搜哪裡，`is:open` 是搜什麼狀態。
2. **「`no:` 找空缺，`-` 排除惡」** — `no:assignee` 找沒人領的、`-author:bot` 排除 bot。
3. **「`@me` 是替身，自動代入你的帳號」** — `author:@me` / `review-requested:@me` 都是個人專屬待辦清單。

---

*Sources verified against GitHub Docs and freeCodeCamp on Apr 27, 2026. English descriptions are the official wording from those sources; Chinese descriptions are translations. Content rephrased to comply with GitHub's content policy.*