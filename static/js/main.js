var API='/api';
var allProducts=[];
var siteSettings={};
var categories=[];
var activeCat='all';

function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}

function loadSettings(){
  fetch(API+'/settings').then(function(r){return r.json();}).then(function(s){
    siteSettings=s||{};
    if(s&&s.site_title){
      document.title=s.site_title+' - 喵喵咪丫';
      var logo=document.getElementById('site-logo');
      if(logo)logo.textContent=esc(s.site_title);
    }
    if(s&&s.shop_description){
      var desc=document.getElementById('hero-subtitle');
      if(desc)desc.textContent=esc(s.shop_description);
    }
    var ht=document.getElementById('hero-announcement');
    if(ht)ht.textContent=s&&s.site_title?s.site_title:'喵喵咪丫';
    var img=document.getElementById('shop-logo-img');
    if(img&&s.shop_logo){img.src='/uploads/'+s.shop_logo;img.style.display='inline-block';}
    else if(img){img.style.display='none';}
  }).catch(function(e){console.error(e);});
}

function loadCategories(){
  fetch(API+'/categories').then(function(r){return r.json();}).then(function(cats){
    categories=cats||[];
    renderCatNav();
  }).catch(function(e){console.error(e);});
}

function renderCatNav(){
  var nav=document.getElementById('cat-nav');
  var inner=nav.querySelector('.cat-nav-inner');
  if(!inner)return;
  var existing=inner.querySelectorAll('.cat-btn:not([data-cat="all"])');
  existing.forEach(function(b){b.remove();});
  categories.forEach(function(c){
    var btn=document.createElement('button');
    btn.className='cat-btn';
    btn.setAttribute('data-cat',c.name);
    btn.textContent=c.name;
    btn.onclick=function(){filterByCat(c.name);};
    inner.appendChild(btn);
  });
  nav.style.display='';
}

function filterByCat(cat){
  activeCat=cat;
  document.querySelectorAll('.cat-btn').forEach(function(b){
    b.classList.toggle('active', b.getAttribute('data-cat')===cat);
  });
  renderPage();
}

function loadProducts(){
  fetch(API+'/products').then(function(r){return r.json();}).then(function(prods){
    allProducts=prods||[];
    renderPage();
  }).catch(function(e){console.error(e);});
}

function renderPage(){
  var main=document.getElementById('main-content');
  if(!main)return;
  var displayProds=activeCat==='all'?allProducts:allProducts.filter(function(p){return p.category===activeCat;});
  if(displayProds.length===0){
    main.innerHTML='<p class="loading-text">该分类下暂无商品</p>';
  }else{
    var html='<div class="grid">';
    for(var i=0;i<displayProds.length;i++){html+=buildCard(displayProds[i]);}
    html+='</div>';
    main.innerHTML=html;
  }
}

function buildCard(p){
  var stockClass=p.stock<3?' low':'';
  var html='';
  html+='<div class="card" onclick="goProduct('+p.id+')">';
  html+='<img class="card-img" src="/uploads/'+esc(p.image)+'" alt="'+esc(p.title||p.name)+'" onerror="this.src=\'/uploads/placeholder.jpg\'">';
  html+='<div class="card-body">';
  html+='<div class="card-cat">'+esc(p.category)+'</div>';
  html+='<div class="card-name">'+esc(p.title||p.name)+'</div>';
  html+='<div class="card-price">&#165;'+p.price+'</div>';
  html+='<div class="card-stock'+stockClass+'">库存 '+p.stock+' 件</div>';
  html+='</div></div>';
  return html;
}

function goProduct(id){window.location.href='/product?id='+id;}

function showWechatQR(){
  var modal=document.getElementById('qr-modal');
  var qrImg=document.getElementById('qr-img');
  var qrPh=document.getElementById('qr-placeholder');
  if(siteSettings.wechat_qr){qrImg.src='/uploads/'+siteSettings.wechat_qr;qrImg.style.display='';qrPh.style.display='none';}
  else{qrImg.style.display='none';qrPh.style.display='';}
  modal.classList.add('open');
}
function closeQR(){document.getElementById('qr-modal').classList.remove('open');}

function openOrderQuery(){
  document.getElementById('order-query-email').value='';
  document.getElementById('order-query-password').value='';
  document.getElementById('order-query-result').style.display='none';
  document.getElementById('order-query-result').innerHTML='';
  document.getElementById('order-query-modal').classList.add('open');
}
function closeOrderQuery(){document.getElementById('order-query-modal').classList.remove('open');}

function doQueryOrder(){
  var email=document.getElementById('order-query-email').value.trim().toLowerCase();
  var password=document.getElementById('order-query-password').value;
  if(!email||!password){toast("请输入邮箱和密码");return;}
  if(!/^[0-9]{6,8}$/.test(password)){toast("查询密码为6-8位数字");return;}
  var resultDiv=document.getElementById('order-query-result');
  resultDiv.style.display='block';
  resultDiv.innerHTML='<p style="color:var(--brown-light);text-align:center;">查询中...</p>';
  fetch(API+'/order/query',{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:email,password:password})})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.id){
        var st=d.status==='completed'?'<span style="color:#7BC89A;font-weight:700;">已确认</span>':'<span style="color:#e67e22;font-weight:700;">待付款确认</span>';
        resultDiv.innerHTML='<div style="background:#fff8f0;border-radius:10px;padding:14px;border:1px solid #fce4ec;">'
          +'<p><strong>订单编号：</strong>'+d.id+'</p>'
          +'<p><strong>商品：</strong>'+esc(d.product_name)+'</p>'
          +'<p><strong>数量：</strong>'+d.qty+' 件</p>'
          +'<p><strong>应付金额：</strong><span style="color:var(--pink-dark);font-weight:800;">&#165;'+d.total+'</span></p>'
          +'<p><strong>状态：</strong>'+st+'</p>'
          +'<p style="font-size:0.78rem;color:#aaa;margin-top:8px;">订单保留7天后自动清除</p>'
          +'</div>';
      }else{resultDiv.innerHTML='<p style="color:#e74c3c;text-align:center;">'+esc(d.error||'未找到订单')+'</p>';}
    })
    .catch(function(){resultDiv.innerHTML='<p style="color:#e74c3c;text-align:center;">网络错误</p>';});
}

function toast(msg){
  var t=document.createElement('div');
  t.className='toast';t.textContent=msg;
  document.body.appendChild(t);
  setTimeout(function(){t.classList.add('show');},10);
  setTimeout(function(){t.classList.remove('show');setTimeout(function(){t.remove();},300);},2500);
}

document.addEventListener('DOMContentLoaded',function(){
  loadSettings();
  loadCategories();
  loadProducts();
});
