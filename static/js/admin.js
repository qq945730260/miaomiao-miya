var API="/api";
var isAuthenticated=false;
var products=[];
var settings={};
var categories=[];
var orders=[];
function toImgSrc(v){return v&&v.startsWith("http")?v:(v?"/uploads/"+v:"");}

function toast(msg){
  var t=document.getElementById("toast");
  t.textContent=msg;
  t.classList.add("show");
  setTimeout(function(){t.classList.remove("show");},2500);
}

function login(user,pwd){
  if(!user||!pwd){toast("请输入用户名和密码");return;}
  var btn=document.querySelector("#login-section .btn-pink");
  if(btn){btn.disabled=true;btn.textContent="登录中...";}
  console.log("LOGIN ATTEMPT:", user, pwd.length);
  fetch(API+"/admin/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:user,password:pwd})})
    .then(function(r){
      console.log("LOGIN RESPONSE status:", r.status);
      return r.json();
    })
    .then(function(d){
      console.log("LOGIN DATA:", d);
      if(btn){btn.disabled=false;btn.textContent="登录";}
      if(d.ok){isAuthenticated=true;document.getElementById("login-section").style.display="none";document.getElementById("admin-main").style.display="block";document.getElementById("nav-auth").style.display="flex";loadData();}
      else{toast(d.error||"登录失败");}
    })
    .catch(function(e){
      console.error("LOGIN ERROR:", e);
      if(btn){btn.disabled=false;btn.textContent="登录";}
      toast("网络错误，请检查连接");
    });
}

function logout(){
  isAuthenticated=false;
  document.getElementById("login-section").style.display="block";
  document.getElementById("admin-main").style.display="none";
  document.getElementById("nav-auth").style.display="none";
  window.location.hash="";
}

function loadData(){
  loadSettings();
  loadCategories();
  loadProducts();
  loadOrders();
}

function loadSettings(){
  fetch(API+"/settings").then(function(r){return r.json();}).then(function(d){
    settings=d||{};
    document.getElementById("form-site_title").value=settings.site_title||"";
    document.getElementById("form-shop_description").value=settings.shop_description||"";
    document.getElementById("form-wechat_qr").value=toImgSrc(settings.wechat_qr);
    if(settings.wechat_qr){var q=document.getElementById("settings-qr-preview");q.src=toImgSrc(settings.wechat_qr);q.style.display="";}
    if(settings.wechat_pay_qr){var w=document.getElementById("wechat-pay-preview");w.src=toImgSrc(settings.wechat_pay_qr);w.style.display="";document.getElementById("form-wechat_pay_qr").value=toImgSrc(settings.wechat_pay_qr);}
    if(settings.alipay_qr){var a=document.getElementById("alipay-pay-preview");a.src=toImgSrc(settings.alipay_qr);a.style.display="";document.getElementById("form-alipay_qr").value=toImgSrc(settings.alipay_qr);}
    if(settings.shop_logo){var l=document.getElementById("shop-logo-preview");l.src=toImgSrc(settings.shop_logo);l.style.display="";document.getElementById("form-shop_logo").value=toImgSrc(settings.shop_logo);}
  }).catch(function(e){console.error("loadSettings error:",e);});
}

function loadCategories(){
  console.log("[ADMIN] Loading categories...");
  fetch(API+"/categories").then(function(r){
    console.log("[ADMIN] Categories response status:", r.status);
    return r.json();
  }).then(function(cats){
    categories=cats||[];
    console.log("[ADMIN] categories:",categories.length,categories);
    loadCategoriesUI();
  }).catch(function(e){console.error("categories error:",e);});
  fetch(API+"/orders").then(function(r){return r.json();}).then(function(d){orders=d||[];console.log("[ADMIN] orders:",orders.length);}).catch(function(){});
}

function loadCategoriesUI(){
  var c=document.getElementById("categories-list");
  var h="";
  categories.sort(function(a,b){return a.sort_order-b.sort_order;});
  categories.forEach(function(cat,i){
    var sold=0;
    products.forEach(function(p){if(p.category===cat.name)sold+=p.total_sold||0;});
    h+='<div class="cat-row">'
      +'<input type="text" class="cat-name" value="'+esc(cat.name)+'" data-id="'+cat.id+'">'
      +'<input type="number" class="cat-sort" value="'+cat.sort_order+'" data-id="'+cat.id+'" style="width:50px;">'
      +'<button class="cat-up" onclick="moveCat('+cat.id+',-1)" data-id="'+cat.id+'">&#9650;</button>'
      +'<button class="cat-down" onclick="moveCat('+cat.id+',1)" data-id="'+cat.id+'">&#9660;</button>'
      +'<span class="cat-sold">'+sold+'</span>'
      +'<button class="cat-del-btn" onclick="deleteCategory('+cat.id+')">X</button>'
      +'</div>';
  });
  c.innerHTML=h;
}
function addCategory(){
  var name=prompt("请输入新分类名称：");
  if(!name||!name.trim())return;
  var max=categories.length>0?Math.max.apply(null,categories.map(function(c){return c.sort_order;}))+1:0;
  fetch(API+"/categories",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:name.trim(),sort_order:max})})
    .then(function(r){return r.json();})
    .then(function(d){if(d.id){loadCategories();toast("分类添加成功");}else toast(d.error||"添加失败");})
    .catch(function(){toast("网络错误");});
}
function deleteCategory(id){
  if(!confirm("确认删除此分类？关联商品不会被删除。"))return;
  fetch(API+"/categories?id="+id,{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){categories=categories.filter(function(c){return c.id!==id;});loadCategories();toast("已删除");}else toast(d.error||"删除失败");})
    .catch(function(){toast("网络错误");});
}
function saveCategories(){
  var rows=document.querySelectorAll(".cat-row");
  var updated=[];
  rows.forEach(function(row,i){
    var id=row.querySelector(".cat-name").getAttribute("data-id");
    var name=row.querySelector(".cat-name").value.trim();
    var sort=row.querySelector(".cat-sort").value;
    if(name)updated.push({id:id,name:name,sort_order:parseInt(sort)||i});
  });
  fetch(API+"/categories/batch",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(updated)})
    .then(function(r){return r.json();})
    .then(function(d){toast(d.ok?"排序已保存":"排序失败");loadCategories();})
    .catch(function(){toast("网络错误");});
}

function saveSettings(){
  var body={
    site_title:document.getElementById("form-site_title").value,
    shop_description:document.getElementById("form-shop_description").value,
    wechat_qr:document.getElementById("form-wechat_qr").value,
    wechat_pay_qr:document.getElementById("form-wechat_pay_qr").value,
    alipay_qr:document.getElementById("form-alipay_qr").value,
    shop_logo:document.getElementById("form-shop_logo").value,
  };
  fetch(API+"/settings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){toast("设置已保存");loadSettings();}else toast(d.error||"保存失败");})
    .catch(function(){toast("网络错误");});
}

function loadProducts(){
  fetch(API+"/products").then(function(r){return r.json();}).then(function(d){
    products=d||[];
    renderProducts();
  }).catch(function(e){console.error("products error:",e);});
}

function renderProducts(){
  var c=document.getElementById("products-list");
  var h='';
  products.forEach(function(p){
    var titleHtml=p.title?esc(p.title):'<span style="color:#ccc;font-size:0.8rem;">(无标题)</span>';
    h+='<tr>'
      +'<td><img src="'+toImgSrc(p.image)+'" style="width:50px;height:50px;object-fit:cover;" onerror="this.src=\'/uploads/placeholder.jpg\'"></td>'
      +'<td>'+p.id+'</td>'
      +'<td>'+titleHtml+'</td>'
      +'<td>'+esc(p.name)+'</td>'
      +'<td>'+esc(p.category)+'</td>'
      +'<td>'+p.price+'</td>'
      +'<td>'+p.stock+'</td>'
      +'<td>'+((p.total_sold)||0)+'</td>'
      +'<td><button onclick="editProduct('+p.id+')">编辑</button> <button onclick="deleteProduct('+p.id+')">删除</button></td>'
      +'</tr>';
  });
  c.innerHTML=h||'<tr><td colspan="9">暂无商品</td></tr>';
}

function editProduct(id){
  var p=products.find(function(x){return x.id===id;});
  if(!p)return;
  document.getElementById("form-id").value=p.id;
  document.getElementById("form-title").value=p.title||"";
  document.getElementById("form-name").value=p.name||"";
  document.getElementById("form-category").value=p.category||"";
  document.getElementById("form-price").value=p.price||"";
  document.getElementById("form-stock").value=p.stock||"";
  document.getElementById("form-image").value=p.image||"";
  document.getElementById("form-detail_image").value=p.detail_image||"";
  if(p.detail_image){var dp=document.getElementById("detail-preview-img");dp.src=toImgSrc(p.detail_image);dp.style.display="";}
  document.getElementById("form-desc").value=p.description||"";
  document.getElementById("form-wechat").value=p.wechat||"";
  if(p.image!=="placeholder.jpg"){var prev=document.getElementById("preview-img");prev.src=toImgSrc(p.image);prev.style.display="";}
}

function submitForm(){
  var id=document.getElementById("form-id").value;
  var name=document.getElementById("form-title").value.trim();
  var title=name;
  var cat=document.getElementById("form-category").value.trim();
  var price=parseFloat(document.getElementById("form-price").value)||0;
  var stock=parseInt(document.getElementById("form-stock").value)||0;
  var image=document.getElementById("form-image").value.trim();
  var detail_image=document.getElementById("form-detail_image").value.trim();
  var description=document.getElementById("form-desc").value;
  var wechat=document.getElementById("form-wechat").value.trim();
  if(!name){toast("请填写商品标题");return;}
  if(!price){toast("请填写价格");return;}
  var body={name:name,title:title,category:cat,price:price,stock:stock,image:image,detail_image:detail_image,description:description,wechat:wechat};
  var url=API+(id?"/products?id="+id:"/products");
  var method=id?"PUT":"POST";
  fetch(url,{method:method,headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.id||d.ok){
        toast(id?"商品已更新":"商品已添加");
        document.getElementById("form-id").value="";
        document.getElementById("form-title").value="";
        document.getElementById("form-name").value="";
        document.getElementById("form-category").value="";
        document.getElementById("form-price").value="";
        document.getElementById("form-stock").value="";
        document.getElementById("form-image").value="";
        document.getElementById("form-detail_image").value="";
        document.getElementById("form-desc").value="";
        document.getElementById("form-wechat").value="";
        document.getElementById("preview-img").style.display="none";
        document.getElementById("detail-preview-img").style.display="none";
        loadProducts();
      }else toast(d.error||"保存失败");
    })
    .catch(function(){toast("网络错误");});
}

function deleteProduct(id){
  if(!confirm("确认删除此商品？"))return;
  fetch(API+"/products?id="+id,{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){products=products.filter(function(p){return p.id!==id;});renderProducts();toast("已删除");}
      else toast(d.error||"删除失败");
    })
    .catch(function(){toast("网络错误");});
}

function loadOrders(){
  fetch(API+"/orders").then(function(r){return r.json();}).then(function(d){
    orders=d||[];
    renderOrders();
  }).catch(function(e){console.error("orders error:",e);});
}

function renderOrders(){
  var c=document.getElementById("orders-list");
  var h='';
  orders.sort(function(a,b){return b.id-a.id;});
  orders.forEach(function(o){
    var date=(o.created_at||"").slice(0,10);
    h+='<tr>'
      +'<td>'+o.id+'</td>'
      +'<td>'+esc(o.email)+'</td>'
      +'<td>'+esc(o.product_name)+'</td>'
      +'<td>'+o.quantity+'</td>'
      +'<td>'+o.total+'</td>'
      +'<td>'+date+'</td>'
      +'<td><button onclick="deleteOrder('+o.id+')" style="background:#e74c3c;">删除</button></td>'
      +'</tr>';
  });
  c.innerHTML=h||'<tr><td colspan="7">暂无订单</td></tr>';
}

function deleteOrder(id){
  fetch(API+"/admin/order/delete?id="+id,{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){loadOrders();toast("已删除");}else toast(d.error||"删除失败");})
    .catch(function(){toast("网络错误");});
}

function cleanOrders(){
  if(!confirm("确认清理7天前的过期订单？"))return;
  fetch(API+"/admin/order/clean",{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){loadOrders();toast("已清理");}else toast(d.error||"清理失败");})
    .catch(function(){toast("网络错误");});
}

function uploadShopLogo(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-shop_logo").value=toImgSrc(d.filename);document.getElementById("shop-logo-preview").src=toImgSrc(d.filename);document.getElementById("shop-logo-preview").style.display="";}
    })
    .catch(function(){toast("上传失败");});
}

function uploadQRImage(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-wechat_qr").value=toImgSrc(d.filename);document.getElementById("settings-qr-preview").src=toImgSrc(d.filename);document.getElementById("settings-qr-preview").style.display="";toast("客服二维码上传成功");}
    })
    .catch(function(){toast("上传失败");});
}

function uploadPayQRImage(e,type){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){
        var hid=type==="wechat"?"form-wechat_pay_qr":"form-alipay_qr";
        var pid=type==="wechat"?"wechat-pay-preview":"alipay-pay-preview";
        document.getElementById(hid).value=toImgSrc(d.filename);
        document.getElementById(pid).src=toImgSrc(d.filename);
        document.getElementById(pid).style.display="";
        toast(type==="wechat"?"微信支付收款码上传成功":"支付宝收款码上传成功");
      }
    })
    .catch(function(){toast("上传失败");});
}

function changePassword(){
  var old=document.getElementById("form-old_password").value;
  var nw=document.getElementById("form-new_password").value;
  var cf=document.getElementById("form-confirm_password").value;
  if(!old||!nw||!cf){toast("请填写完整");return;}
  if(nw!==cf){toast("两次密码不一致");return;}
  fetch(API+"/admin/change_password",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({old_password:old,new_password:nw})})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){toast("密码修改成功");document.getElementById("form-old_password").value="";document.getElementById("form-new_password").value="";document.getElementById("form-confirm_password").value="";}else toast(d.error||"修改失败");})
    .catch(function(){toast("网络错误");});
}

function uploadImage(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-image").value=toImgSrc(d.filename);document.getElementById("preview-img").src=toImgSrc(d.filename);document.getElementById("preview-img").style.display="";}
    })
    .catch(function(){toast("上传失败");});
}

function uploadDetailImage(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-detail_image").value=toImgSrc(d.filename);document.getElementById("detail-preview-img").src=toImgSrc(d.filename);document.getElementById("detail-preview-img").style.display="";toast("详情图上传成功");}
    })
    .catch(function(){toast("上传失败");});
}

function updateDetailRatio(){}

function esc(s){return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function showTab(name){
  document.querySelectorAll(".tab-content").forEach(function(el){el.style.display="none";});
  document.querySelectorAll(".nav-tab").forEach(function(el){el.classList.remove("active");});
  document.getElementById("tab-"+name).style.display="block";
  event.target.classList.add("active");
}
