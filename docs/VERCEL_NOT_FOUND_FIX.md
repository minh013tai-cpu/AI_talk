# Giải quyết lỗi Vercel NOT_FOUND (404)

## 1. Cách sửa đã áp dụng

### Đã thêm `vercel.json` tại thư mục gốc dự án

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Cấu hình Vercel Project (bắt buộc vì đây là monorepo):**

- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

Nếu bạn deploy từ repo root mà không đặt Root Directory = `frontend`, Vercel sẽ không tìm thấy `package.json`/framework → dễ dẫn tới NOT_FOUND hoặc build lỗi.

---

## 2. Nguyên nhân gốc rễ

### Code đang làm gì vs. điều cần làm

| Thực tế (trước khi sửa) | Mong muốn |
|-------------------------|-----------|
| User vào `/journal` → Vercel nhận request path = `/journal` → tìm **file** tên `journal` hoặc `journal.html` trong thư mục build → **không có** → trả 404 NOT_FOUND | Mọi path như `/`, `/journal`, `/memory` đều phải trả về **cùng một file** `index.html`, sau đó React Router trong trình duyệt quyết định hiển thị component nào |

### Điều kiện gây ra lỗi

1. **Client-side routing (React Router)**  
   Ứng dụng có các route: `/`, `/journal`, `/memory`. Đây là route **ảo** trong browser, không phải file/folder thật trên server.

2. **Request trực tiếp hoặc refresh**  
   - User gõ URL `https://your-app.vercel.app/journal`  
   - Hoặc đang ở `/journal` rồi nhấn F5  

   Lúc này trình duyệt gửi **một request HTTP** tới server với path = `/journal`. Server (Vercel) không biết React Router, chỉ thấy “cần trả nội dung cho path `/journal`” → tìm file tương ứng → không có → 404.

3. **Không có rewrite**  
   Không có `vercel.json` với `rewrites` nên Vercel xử lý mọi path như request tới file tĩnh. Chỉ có path `/` mới khớp `index.html`, các path khác đều 404.

### Sai lầm / quan niệm sai

- Nghĩ rằng “route React” = “URL trên server”: thực tế server chỉ nhìn thấy path của HTTP request, không biết React Router.
- Nghĩ rằng chỉ cần build frontend là đủ: với SPA dùng client-side routing, **server** phải được cấu hình để “mọi path không phải file tĩnh đều trả về `index.html`”.

---

## 3. Khái niệm nền tảng

### Vì sao lỗi này tồn tại và nó “bảo vệ” bạn thế nào?

- **404 NOT_FOUND** là chuẩn HTTP: “tài nguyên tại URL này không tồn tại”. Server đang làm đúng nghĩa khi không tìm thấy file cho path đó.
- Nó bảo vệ bạn khỏi việc trả nhầm nội dung: nếu không có cơ chế rõ ràng (rewrite), việc trả `index.html` cho mọi path có thể gây nhầm lẫn nếu sau này bạn có API hoặc file thật tại path tương tự.

### Mental model đúng

1. **Hai “thế giới” routing**
   - **Server (Vercel)**: nhận request → có file tĩnh thì trả file, không thì có thể **rewrite** sang một URL khác (ở đây là `/index.html`).
   - **Client (React Router)**: sau khi nhận `index.html` + JS, đọc `window.location.pathname` (ví dụ `/journal`) và render đúng component.

2. **SPA = một entry point**  
   Mọi “trang” thực chất là cùng một trang HTML; “đổi trang” là đổi component trong JS, không phải server trả nhiều file HTML khác nhau.

3. **Thứ tự xử lý trên Vercel**  
   - Ưu tiên: nếu path khớp **file có trong Output (vd. `dist`)** → trả file (vd. `/assets/xxx.js`).  
   - Nếu không có file → mới áp dụng **rewrites** → ở đây trả `/index.html`.

### Vị trí trong thiết kế framework / ngôn ngữ

- **React Router** chỉ chạy trên client, không can thiệp vào cách server trả response.
- **Vercel** là server/hosting: cần cấu hình (rewrites) để phù hợp với mô hình SPA “một entry point”.
- Mọi nền tảng host SPA (Netlify, Firebase Hosting, Nginx, etc.) đều cần cấu hình tương tự: “fallback to index.html”.

---

## 4. Dấu hiệu cảnh báo để tránh lặp lại

### Cần để ý

- Dự án dùng **React Router / Vue Router / client-side routing** và deploy lên **static / serverless host** → luôn kiểm tra có **fallback/rewrite về index.html** chưa.
- Có route **không phải `/`** (vd. `/journal`, `/memory`) → test: mở trực tiếp URL đó và refresh; nếu 404 thì thiếu cấu hình server.
- Monorepo (backend + frontend): cần chỉ rõ **Root Directory** trỏ đúng thư mục frontend (vd. `frontend`) để Vercel build đúng và tìm thấy `index.html` trong `dist`.

### Sai lầm tương tự có thể gặp

- Deploy SPA lên Nginx/Apache mà không cấu hình `try_files` / fallback → 404 khi refresh hoặc vào sâu URL.
- Dùng **HashRouter** (`#/journal`) thì URL không gửi path lên server → không 404 nhưng SEO và URL đẹp kém hơn; đổi sang **BrowserRouter** mà không cấu hình server → dễ gặp lại 404.

### Code smell / pattern

- Có `<Router>`, `<Routes>`, `<Route>` nhưng **không có** file cấu hình deploy (vd. `vercel.json`, `netlify.toml`, `_redirects`) cho SPA.
- README chỉ nói “chạy npm run build” mà không nói “cấu hình host fallback về index.html” và “Root Directory” (nếu monorepo).

---

## 5. Các cách làm khác và đánh đổi

| Cách làm | Ưu | Nhược |
|----------|----|--------|
| **Rewrites trong vercel.json** (đã dùng) | Chuẩn, rõ ràng, dễ đọc; tương thích tốt với Vercel. | Chỉ áp dụng khi deploy trên Vercel. |
| **HashRouter** (`#/journal`) | Không cần cấu hình server; không 404 khi refresh. | URL có `#`, SEO kém, chia sẻ link kém chuẩn. |
| **Server-Side Rendering (SSR)** (Next.js, Remix, etc.) | Mỗi URL có thể trả HTML riêng, tốt cho SEO. | Đổi stack, phức tạp hơn, không còn “static SPA thuần”. |
| **Cấu hình tương tự trên host khác** (Netlify `_redirects`, Nginx `try_files`) | Cùng mental model, chỉ khác cú pháp. | Phải nhớ cấu hình đúng cho từng nền tảng. |

**Kết luận:** Với SPA React + Vite hiện tại, dùng **rewrites trong vercel.json** là cách phù hợp và ít thay đổi code nhất.

---

## Tóm tắt

- **Đã làm:** Thêm `vercel.json` với `rewrites` trỏ mọi path không khớp file tĩnh về `/index.html`; cần đặt Root Directory = `frontend` trong Vercel.
- **Chưa làm:** Không đổi code React, không đổi logic API; chỉ bổ sung cấu hình deploy và tài liệu này.
- **Nguyên nhân:** SPA dùng client-side routing nhưng server không được cấu hình fallback → request tới `/journal`, `/memory` bị xử lý như request file → 404.
- **Ý tưởng cần nhớ:** SPA = một entry point; server phải “fallback to index.html” cho mọi path không phải file tĩnh; React Router chỉ chạy sau khi đã load `index.html`.
