var API="/api";
var isAuthenticated=false;
var products=[];
var settings={};
var categories=[];
var orders=[];

function toast(msg){
  var t=document.getElementById("toast");
  t.textContent=msg;
  t.classList.add("show");
  setTimeout(function(){t.classList.remove("show");},2500);
}

function login(user,pwd){
  if(!user||!pwd){toast("请输入用户名和密码");return;}
  fetch(API+"/admin/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:user,password:pwd})})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.ok){isAuthenticated=true;document.getElementById("login-section").style.display="none";document.getElementById("admin-main").style.display="block";document.getElementById("nav-auth").style.display="flex";loadData();}
      else{toast(d.error||"登录失败");}
    })
    .catch(function(){toast("网络错误");});
}

function logout(){
  document.cookie="session=;Path=/;Expires=Thu, 01 Jan 1970 00:00:00 GMT";
  location.href="/admin";
}

function loadData(){
  Promise.all([fetch(API+"/products"),fetch(API+"/settings"),fetch(API+"/categories"),fetch(API+"/orders")])
    .then(function(rs){return Promise.all(rs.map(function(r){return r.json();}));})
    .then(function(data){
      products=data[0]||[];
      settings=data[1]||{};
      categories=data[2]||[];
      orders=data[3]||[];
      renderTable();
      loadSettings();
      loadCategories();
      renderOrders();
    });
}

function renderTable(){
  document.getElementById("product-count").textContent=products.length;
  var tbody=document.getElementById("product-table-body");
  if(!tbody)return;
  var html="";
  for(var i=0;i<products.length;i++){
    var p=products[i];
    var titleHtml=p.title?esc(p.title):'<span style="color:#ccc;font-size:0.8rem;">(无标题)</span>';
    html+='<tr>'
      +'<td><img src="/uploads/'+esc(p.image)+'" onerror="this.src=\'/uploads/placeholder.jpg\'"></td>'
      +'<td>'+p.id+'</td>'
      +'<td>'+titleHtml+'</td>'
      +'<td>'+esc(p.name)+'</td>'
      +'<td>'+esc(p.category)+'</td>'
      +'<td>'+p.price+'</td>'
      +'<td>'+p.stock+'</td>'
      +'<td><button class="trash-btn" onclick="editProduct('+p.id+')">编辑</button> <button class="trash-btn" onclick="deleteProduct('+p.id+')">删除</button></td>'
      +'</tr>';
  }
  tbody.innerHTML=html;
}

function renderOrders(){
  document.getElementById("order-count").textContent=orders.length;
  var tbody=document.getElementById("order-table-body");
  if(!tbody)return;
  var html="";
  for(var i=0;i<orders.length;i++){
    var o=orders[i];
    var st=o.status==="completed"?'<span style="color:#7BC89A;font-weight:700;">已确认</span>':'<span style="color:#e67e22;font-weight:700;">待确认</span>';
    html+='<tr>'
      +'<td>'+(o.order_number||o.id)+'</td>'
      +'<td>'+(o.product_title?esc(o.product_title):esc(o.product_name))+'</td>'
      +'<td style="font-size:0.8rem;">'+esc(o.email)+'</td>'
      +'<td>'+o.qty+'</td>'
      +'<td>&#165;'+o.total+'</td>'
      +'<td>'+st+'</td>'
      +'<td style="font-size:0.78rem;">'+esc(o.created_at)+'</td>'
      +'<td>';
    if(o.status==="pending"){
      html+='<button class="btn btn-sm btn-pink" onclick="confirmOrder('+o.id+')" style="padding:3px 8px;font-size:0.75rem;">确认</button> ';
      html+='<button class="trash-btn" onclick="deleteOrder('+o.id+')" style="padding:3px 8px;font-size:0.75rem;">删除</button>';
    }
    html+='</td></tr>';
  }
  tbody.innerHTML=html||'<tr><td colspan="8" style="text-align:center;color:#aaa;">暂无订单</td></tr>';
}

function confirmOrder(id){
  if(!confirm("确认该订单已付款？将自动扣减库存。"))return;
  fetch(API+"/admin/order/confirm",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({order_id:id})})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){toast("已确认，库存已扣减");loadData();}else toast(d.error||"操作失败");})
    .catch(function(){toast("网络错误");});
}

function deleteOrder(id){
  if(!confirm("确定删除该订单？"))return;
  fetch(API+"/admin/order/delete?id="+id,{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){toast("已删除");loadData();}else toast(d.error||"删除失败");})
    .catch(function(){toast("网络错误");});
}

function cleanOrders(){
  fetch(API+"/admin/order/clean",{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){toast(d.ok?"已清理过期订单":"清理失败");loadData();})
    .catch(function(){toast("网络错误");});
}

function loadSettings(){
  document.getElementById("form-site_title").value=settings.site_title||"";
  document.getElementById("form-site_tagline").value=settings.site_tagline||"";
  document.getElementById("form-wechat_qr").value=settings.wechat_qr||"";
  if(settings.wechat_qr){var q=document.getElementById("settings-qr-preview");q.src="/uploads/"+settings.wechat_qr;q.style.display="";}
  if(settings.wechat_pay_qr){var w=document.getElementById("wechat-pay-preview");w.src="/uploads/"+settings.wechat_pay_qr;w.style.display="";document.getElementById("form-wechat_pay_qr").value=settings.wechat_pay_qr;}
  if(settings.alipay_qr){var a=document.getElementById("alipay-pay-preview");a.src="/uploads/"+settings.alipay_qr;a.style.display="";document.getElementById("form-alipay_qr").value=settings.alipay_qr;}
}

function loadCategories(){
  fetch(API+"/categories").then(function(r){return r.json();}).then(function(cats){
    categories=cats||[];
    renderCatList();
  });
}
function renderCatList(){
  var c=document.getElementById("cat-list");
  if(!c)return;
  var h="";
  categories.forEach(function(cat,i){
    h+='<div class="cat-row" data-id="'+cat.id+'">'
      +'<span class="cat-order">'+(i+1)+'</span>'
      +'<input type="text" class="cat-name-input" value="'+esc(cat.name)+'" data-id="'+cat.id+'">'
      +'<input type="number" class="cat-sort-input" value="'+cat.sort_order+'" data-id="'+cat.id+'" style="width:50px;">'
      +'<button class="cat-del-btn" onclick="deleteCategory('+cat.id+')">X</button>'
      +'</div>';
  });
  c.innerHTML=h;
}
function addCategory(){
  var name=prompt("请输入分类名称：");
  if(!name||!name.trim())return;
  var max=categories.length>0?Math.max.apply(null,categories.map(function(c){return c.sort_order;}))+1:0;
  fetch(API+"/categories",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:name.trim(),sort_order:max})})
    .then(function(r){return r.json();})
    .then(function(d){if(d.id){loadCategories();toast("分类已添加");}else toast(d.error||"添加失败");})
    .catch(function(){toast("网络错误");});
}
function deleteCategory(id){
  if(!confirm("确定删除该分类？关联商品不会被删除。"))return;
  fetch(API+"/categories?id="+id,{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){loadCategories();toast("已删除");}else toast(d.error||"删除失败");})
    .catch(function(){toast("网络错误");});
}
function saveCategories(){
  var rows=document.querySelectorAll(".cat-row");
  var updated=[];
  rows.forEach(function(row){
    var id=parseInt(row.getAttribute("data-id"));
    var nameEl=row.querySelector(".cat-name-input");
    var sortEl=row.querySelector(".cat-sort-input");
    if(id&&nameEl&&sortEl){
      updated.push({id:id,name:nameEl.value.trim(),sort_order:parseInt(sortEl.value)||0});
    }
  });
  if(updated.length===0){toast("没有可保存的分类");return;}
  fetch(API+"/categories",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({categories:updated})})
    .then(function(r){return r.json();})
    .then(function(d){toast(d.ok?"分类已保存":"保存失败");loadCategories();})
    .catch(function(){toast("网络错误");});
}

function saveSettings(){
  var body={
    site_title:document.getElementById("form-site_title").value,
    shop_description:document.getElementById("form-shop_description").value,
    wechat_qr:document.getElementById("form-wechat_qr").value,
    wechat_pay_qr:document.getElementById("form-wechat_pay_qr").value,
    alipay_qr:document.getElementById("form-alipay_qr").value,
    shop_logo:document.getElementById("form-shop_logo").value
  };
  fetch(API+"/settings",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})
    .then(function(r){return r.json();})
    .then(function(d){toast(d.ok?"设置已保存":"保存失败");})
    .catch(function(){toast("网络错误");});
}

function uploadShopLogo(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-shop_logo").value=d.filename;document.getElementById("shop-logo-preview").src="/uploads/"+d.filename;document.getElementById("shop-logo-preview").style.display="";}
    })
    .catch(function(){toast("上传失败");});
}

function uploadQRImage(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-wechat_qr").value=d.filename;document.getElementById("settings-qr-preview").src="/uploads/"+d.filename;document.getElementById("settings-qr-preview").style.display="";toast("二维码图片上传成功");}
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
        document.getElementById(hid).value=d.filename;
        document.getElementById(pid).src="/uploads/"+d.filename;
        document.getElementById(pid).style.display="";
        toast(type==="wechat"?"微信收款码上传成功":"支付宝收款码上传成功");
      }
    })
    .catch(function(){toast("上传失败");});
}

function changePassword(){
  var old=document.getElementById("form-old_password").value;
  var nw=document.getElementById("form-new_password").value;
  var cf=document.getElementById("form-confirm_password").value;
  if(!old||!nw){toast("请填写完整");return;}
  if(nw!==cf){toast("两次密码不一致");return;}
  if(nw.length<4){toast("密码至少4位");return;}
  fetch(API+"/admin/change_password",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({old_password:old,new_password:nw})})
    .then(function(r){return r.json();})
    .then(function(d){if(d.ok){toast("密码已修改");}else{toast(d.error||"旧密码错误");}})
    .catch(function(){toast("网络错误，请检查连接");});
}

function populateCategorySelect(){
  var sel=document.getElementById("form-category");
  if(!sel)return;
  sel.innerHTML='<option value="">请选择分类</option>';
  categories.forEach(function(c){
    var opt=document.createElement("option");
    opt.value=c.name; opt.textContent=c.name;
    sel.appendChild(opt);
  });
}

function openModal(mode,id){
  document.getElementById("modal").classList.add("open");
  document.getElementById("modal-title").textContent=mode==="add"?"新增商品":"编辑商品";
  populateCategorySelect();
  if(mode==="edit"&&id!==undefined){
    var p=null;
    for(var i=0;i<products.length;i++){if(products[i].id===id){p=products[i];break;}}
    if(p){
      document.getElementById("form-id").value=p.id;
      document.getElementById("form-title").value=p.title||"";
      document.getElementById("form-category").value=p.category;
      document.getElementById("form-price").value=p.price;
      document.getElementById("form-stock").value=p.stock;
      document.getElementById("form-image").value=p.image;
      document.getElementById("form-detail_image").value=p.detail_image||"";
      if(p.detail_image){var dp=document.getElementById("detail-preview-img");dp.src="/uploads/"+p.detail_image;dp.style.display="";}
      document.getElementById("form-desc").value=p.description||"";
      document.getElementById("form-wechat").value=p.wechat||"";
      if(p.image!=="placeholder.jpg"){var prev=document.getElementById("preview-img");prev.src="/uploads/"+p.image;prev.style.display="";}
    }
  }else{
    document.getElementById("form-id").value="";
    document.getElementById("form-title").value="";
    document.getElementById("form-price").value="";
    document.getElementById("form-stock").value="";
    document.getElementById("form-image").value="placeholder.jpg";
    document.getElementById("form-detail_image").value="";
    document.getElementById("detail-preview-img").style.display="none";
    document.getElementById("form-desc").value="";
    document.getElementById("form-wechat").value="";
    document.getElementById("preview-img").style.display="none";
  }
}

function closeModal(){document.getElementById("modal").classList.remove("open");}
function editProduct(id){openModal("edit",id);}

function deleteProduct(id){
  if(!confirm("确定删除该商品？"))return;
  fetch(API+"/products?id="+id,{method:"DELETE"})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.ok){products=products.filter(function(p){return p.id!==id;});renderTable();toast("已删除");}
      else toast(d.error||"删除失败");
    })
    .catch(function(){toast("网络错误");});
}

function uploadImage(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-image").value=d.filename;document.getElementById("preview-img").src="/uploads/"+d.filename;document.getElementById("preview-img").style.display="";}
    })
    .catch(function(){toast("上传失败");});
}

function uploadDetailImage(e){
  var file=e.target.files[0];if(!file)return;
  var fd=new FormData();fd.append("image",file);
  fetch(API+"/upload",{method:"POST",body:fd})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.filename){document.getElementById("form-detail_image").value=d.filename;document.getElementById("detail-preview-img").src="/uploads/"+d.filename;document.getElementById("detail-preview-img").style.display="";toast("详情图上传成功");}
    })
    .catch(function(){toast("上传失败");});
}

function updateDetailRatio(){}

function submitForm(){
  var id=document.getElementById("form-id").value;
  var name=document.getElementById("form-title").value.trim();
  var title=name;
  var cat=document.getElementById("form-category").value;
  var price=parseFloat(document.getElementById("form-price").value);
  var stock=parseInt(document.getElementById("form-stock").value)||0;
  var image=document.getElementById("form-image").value;
  var detail_image=document.getElementById("form-detail_image").value;
  var desc=document.getElementById("form-desc").value.trim();
  var wechat=document.getElementById("form-wechat").value.trim();
  if(!name){toast("请填写商品标题");return;}
  if(isNaN(price)||price<=0){toast("请填写正确价格");return;}
  if(!cat){toast("请选择分类");return;}
  var body={name:name,title:title,category:cat,price:price,stock:stock,image:image,detail_image:detail_image,description:desc,wechat:wechat,qq:""};
  var method=id?"PUT":"POST";
  var url=id?API+"/products?id="+id:API+"/products";
  fetch(url,{method:method,headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.id){
        if(id){for(var i=0;i<products.length;i++){if(products[i].id===parseInt(id)){products[i]=d;break;}}}
        else products.push(d);
        closeModal();renderTable();
        toast(d.id?"保存成功":"新增成功");
      }else{toast(d.error||"操作失败");}
    })
    .catch(function(){toast("网络错误");});
}

function esc(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML;}

fetch(API+"/admin/check")
  .then(function(r){return r.json();})
  .then(function(d){
    if(d.auth){
      document.getElementById("login-section").style.display="none";
      document.getElementById("admin-main").style.display="block";
      document.getElementById("nav-auth").style.display="flex";
      isAuthenticated=true;
      loadData();
    }
  })
  .catch(function(){});
