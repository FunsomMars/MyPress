#!/usr/bin/env python
"""
导入WordPress页面数据到Wagtail
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_press.settings.dev')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from home.models import CustomPage, HomePage
from wagtail.models import Page
from django.utils.text import slugify
from datetime import datetime

# WordPress页面数据（从SQL文件中提取）
PAGES_DATA = [
    {
        'title': '日常随笔',
        'slug': 'essay',
        'content': '''<!-- wp:image -->
<figure class="wp-block-image"><img src="/media/2017/04/9.jpg" alt=""/><figcaption>Essay</figcaption></figure>
<!-- /wp:image -->

<!-- wp:audio -->
<figure class="wp-block-audio"><audio controls src="/media/2017/04/α·Pav-秋～華恋～.mp3"></audio><figcaption>秋～華恋～</figcaption></figure>
<!-- /wp:audio -->

<!-- wp:list {"ordered":true} -->
<ol><li>与君初相识，犹如故人归；<br>天涯明月新，朝暮最相思。</li><li>一身诗意千寻瀑，万古人间四月天。</li><li>未遇青梅，青梅枯萎，芬芳满地叹繁华；不见竹马，竹马老去，相思万里夜未寐；从此，我爱上的人都像你。</li><li>人有两只眼睛、两只手、两只脚，但为什么人只有一颗心呢？因为另一颗心在另一个人心上。人就是要花一辈子的经历去寻找另一颗心。即使世事再不完美，我也要在如歌的岁月中，找到你。</li><li>爱了就爱了，无悔付出，全心全意；散了就散了，一别两宽，各生欢喜。不必费尽心力去否定曾经的自己，也不必用尽手段去伤害曾经温暖过你的那个人。爱就算不在了，也别变成恨。能与自己讲和，与曾经讲和，这样的分手状态才能决定你今后的人生，能赢。昔日红泥小火炉，今朝千山寒飞雪。评判人品优与劣，全在世人一念间。人生难测，缘起缘灭，若还能在街角相遇，也能心平气和地打声招呼：哦，原来你也在这里。</li><li>你的内心已经兵荒马乱天翻地覆了，可是在别人看来你只是比平时沉默了一点，没人会觉得奇怪。这种战争，注定单枪匹马。<br>一个人，也要活得像一支队伍，<br>不然，寂寞的时候，连买siri的钱都没有。<br>不想做一些事没有人陪伴，殊不知，陪着你的人也不一定理解你。</li><li>人有三样东西是无法隐瞒的，咳嗽、穷困和爱，你想隐瞒越欲盖弥彰；人有三样东西是不该挥霍的，身体、金钱和爱，你想挥霍却得不偿失；人有三样东西是无法挽留的，时间、生命和爱，你想挽留却渐行渐远；人有三样东西是不该回忆的，灾难、死亡和爱，你想回忆却苦不堪言。 ——《洛丽塔》</li><li>愿你乘风破浪，历尽千帆，归来仍少年。</li><li>我们从出生开始就被灌输仇恨教育，年纪稍长要学习丛林法则，社会的现实唯金钱至上。太多的人学不会包容、爱、礼貌、微笑和对生命的尊重。</li><li>人生在世很多时候不光是拼学习的，还要拼忍耐力，情商，人际交往能力，和谁命长，很多寒门学子以为只要就学习好就完事了，世界哪有那么简单。</li><li>有工作的地方没有家，有家的地方却没有工作，他乡容纳不下灵魂，故乡安置不了肉身，一个叫家的地方找不到养家糊口的路，找到了养家糊口的地方却安不了家，从此便有了漂泊，有了远方，有了乡愁。</li><li>如果天总也不亮，那就摸黑过生活;<br>如果发出声音是危险的，那就保持沉默;<br>如果自觉无力发光，那就别去照亮别人。<br>但是——不要习惯了黑暗就为黑暗辩护;<br>不要为自己的苟且而得意洋洋;<br>不要嘲讽那些比自己更勇敢、更有热量的人们。<br>可以卑微如尘土，不可扭曲如蛆虫！</li><li>自古以来，领军为将者，首先要做到的就是赏罚公平，得当。一个能给士兵恩惠的将领才能在关键时刻号令三军无所不往。企业也是如此。作为一个最高决策者，要明白，下面的人想的是什么，需要什么。<br>新的一年开始了。</li><li>寒枝疏干，烟薄景曛，在这新年第一天，回望岁月匆忙行远，有如梦里明灭。 <br>只希望，无论记忆怎样裁剪，我们还能久久地、清晰地、出现在彼此生命中。 <br>也许将来，少的是金风玉露，多的是银汉迢迢，最终是你的天高地远，我的一隅静谧。 <br>也拟仿伊宫徵误，相思只在，眉间度。 <br>只是，这又有何妨呢？ <br>时光正好，琼姈似月，爱恨成酒，风雨当歌。 <br>我知道，有一种只可自品的温暖，便是每次回首时，都能看到，心心念之的她，在不远处微笑粲然，宛如从心底嫣然绽放的灵花，干净清凉，刹那永恒。</li><li>You should try to figure out what you're most passionate about in life, and what you're good at, and the mixture between those two. Then you should give it all your time and have to work really hard, if you wanna get somewhere, with whatever you do, if you work hard enough, you're gonna succeed.</li></ol>''',
        'date': '2017-03-19'
    },
    {
        'title': '关于小孟',
        'slug': 'about',
        'content': '''<!-- wp:paragraph --><p>工程师🧑‍💻，爱好前沿科技行业软件、硬件，以及代码编程💻</p><!-- /wp:paragraph --><!-- wp:image {"id":1516,"linkDestination":"media"} --><figure class="wp-block-image"><a href="/media/2019/03/IMG_7467.jpg"><img src="/media/2019/03/IMG_7467-1024x768.jpg" alt="" class="wp-image-1516"/></a><figcaption>Life is Fantastic</figcaption></figure><!-- /wp:image --><!-- wp:audio {"id":366} --><figure class="wp-block-audio"><audio controls src="/media/2017/04/Coldplay-Yellow.mp3"></audio></figure><!-- /wp:audio --><!-- wp:list --><ul><li>优酷主页（Youku）：<a rel="noreferrer noopener" href="https://i.youku.com/shuaismng" target="_blank">https://i.youku.com/shuaismng</a></li><li>新浪微博（Weibo）：<a rel="noreferrer noopener" href="https://weibo.com/shuaismeng" target="_blank">https://weibo.com/shuaismeng</a></li><li>Bilibili: <a href="https://space.bilibili.com/273841932">https://space.bilibili.com/273841932</a></li><li>Facebook: <a rel="noreferrer noopener" href="https://facebook.com/shuaishuaimeng" target="_blank">https://facebook.com/shuaishuaimeng</a></li><li>Twitter:&nbsp;<a rel="noreferrer noopener" href="https://twitter.com/North_Mars_" target="_blank">https://twitter.com/North_Mars_</a></li></ul>''',
        'date': '2017-03-19'
    },
    {
        'title': '视频剪辑',
        'slug': 'video',
        'content': '''<ol>
    <li><strong>通用笔记本拆机清灰教程</strong><iframe src="https://player.youku.com/embed/XNjk2MjI4MzUy" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>相山公园游玩</strong><iframe src="https://player.youku.com/embed/XMjUwNjk0MzU5Mg==" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>物理学院2015届光伏班毕业生晚会暖场视频</strong><iframe src="https://player.youku.com/embed/XMTg1ODI0ODQ2OA==" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>青春修炼手册歌舞（物理学院2015届光伏班毕业生晚会节目）</strong><iframe src="https://player.youku.com/embed/XMjUwNDE1NzcwMA==" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>穿越火线玩具城堡TD飞毛腿</strong><iframe src="https://player.youku.com/embed/XMTgyMjE4NzQzNg==" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>节奏大师黑暗王子4K HD小师妹AC</strong><iframe src="https://player.youku.com/embed/XNzIyMjkxOTA0" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>节奏大师bad apple（坏苹果）4K HD APC</strong><iframe src="https://player.youku.com/embed/XNzkxMzE2ODQ4" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>节奏大师purple passion （紫色激情）4K HD AC</strong><iframe src="https://player.youku.com/embed/XNzkxMzMyMjIw" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>节奏大师Toy War （玩具战争）4K HD APC</strong><iframe src="https://player.youku.com/embed/XNzkxMzQzNjMy" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>节奏大师 Luv letter（情书） 4K HD SSS</strong><iframe src="https://player.youku.com/embed/XNzk4MDQyMDQ4" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>节奏大师"两根火腿肠的传奇"之DADADA 4K HD SS</strong><iframe src="https://player.youku.com/embed/XODI0NTg0OTgw" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>微电影《大学第一课》</strong><iframe src="https://player.youku.com/embed/XMjY4OTkxMjQ5Ng==" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>Butterfly之电吉他版本</strong><iframe src="https://player.youku.com/embed/XMzYyMTAxOTI0MA==" width="510" height="498" frameborder="0" allowfullscreen="allowfullscreen"></iframe></li>
    <li><strong>天空之城摇滚版</strong><iframe src="https://player.youku.com/embed/XMzYzNzQxNTc4NA==" height="498" width="510" frameborder="0"></iframe></li>
</ol>''',
        'date': '2017-03-23'
    },
    {
        'title': '云音乐歌单',
        'slug': 'cloudmusic',
        'content': '''<ol>
    <li><strong>写作业专用</strong><iframe src="//music.163.com/outchain/player?type=0&id=630819893&auto=0&height=430" width="330" height="450" frameborder="no" marginwidth="0" marginheight="0"></iframe></li>
    <li><strong>跑步健身专用</strong><iframe src="//music.163.com/outchain/player?type=0&id=625440020&auto=0&height=430" width="330" height="450" frameborder="no" marginwidth="0" marginheight="0"></iframe></li>
    <li><strong>睡前专用</strong><iframe src="//music.163.com/outchain/player?type=0&id=607278341&auto=0&height=430" width="330" height="450" frameborder="no" marginwidth="0" marginheight="0"></iframe></li>
    <li><strong>适合婚礼的英文歌曲</strong><iframe src="//music.163.com/outchain/player?type=0&id=601999951&auto=0&height=430" width="330" height="450" frameborder="no" marginwidth="0" marginheight="0"></iframe></li>
    <li><strong>Life(生活)</strong><iframe src="//music.163.com/outchain/player?type=0&id=567494921&auto=0&height=430" width="330" height="450" frameborder="no" marginwidth="0" marginheight="0"></iframe></li>
    <li><strong>Horizon（地平线）</strong><iframe src="//music.163.com/outchain/player?type=0&id=557183985&auto=0&height=430" width="330" height="450" frameborder="no" marginwidth="0" marginheight="0"></iframe></li>
</ol>''',
        'date': '2017-04-02'
    },
    {
        'title': '学点Linux',
        'slug': 'debian',
        'content': '''<!-- wp:image {"id":416,"linkDestination":"custom"} -->
<figure class="wp-block-image"><a href="/media/2017/04/18.jpg"><img src="/media/2017/04/18.jpg" alt="" class="wp-image-416"/></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p><strong>关于Shell in Debian "jessie" X64</strong></p>
<!-- /wp:paragraph -->

<!-- wp:list {"start":1} -->
<ul start="1"><li><strong>cd命令：进入某一个目录</strong></li></ul>
<!-- /wp:list -->

<pre class="wp-block-syntaxhighlighter-code">cd [dir]</pre>

<ul><li><strong>pwd命令：显示当前的工作目录</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">pwd</pre>

<ul><li><strong>mv命令：文件改名、移动文件</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">mv [options] source dest
mv [options] source directory</pre>

<ul><li><strong>rm命令：删除文件及目录</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">rm [options] name</pre>

<ul><li><strong>mkdir命令：创建文件目录</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">mkdir [options] [dir]</pre>

<ul><li><strong>cp命令：将一个文件复制至另一个文件、将目录下数个文件复制到另一个目录</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">cp [options] source dest
cp [options] source directory</pre>

<ul><li><strong>ls命令：列出目录下的内容</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">ls [options] [dir]</pre>

<ul><li><strong>chmod命令：改变文件权限</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">chmod [options] mode file</pre>

<ul><li><strong>chown命令：改变文件属主</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">chown [options] user [:group] file</pre>

<ul><li><strong>apt-get 命令：APT软件包管理工具</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">apt-get [options] command
apt-get [options] install|remove pkg_name1 pkg_name2 pkg_name3...</pre>

<ul><li><strong>whereis命令：查找某个文件或程序</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">whereis [options] file</pre>

<ul><li><strong>unzip命令：解压.zip压缩文件</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">unzip [options] file.zip</pre>

<ul><li><strong>gzip命令：压缩成以.gz结尾的文件</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">gzip [options] file</pre>

<ul><li><strong>tar命令：压缩一个文件或者文件目录下的内容</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">tar [options] file</pre>

<ul><li><strong>Debian切换默认桌面环境</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">update-alternatives --config x-session-manager</pre>

<ul><li><strong>查看系统版本发行商信息</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">lsb_release -a</pre>

<ul><li><strong>VPS一键测试脚本</strong></li></ul>

<pre class="wp-block-syntaxhighlighter-code">wget -qO- bench.sh | bash</pre>''',
        'date': '2017-04-06'
    },
    {
        'title': '段子手段子',
        'slug': 'joke',
        'content': '''<a href="/media/2018/01/make-someone-smile-everyday.jpg"><img class="wp-image-672 size-full alignnone" src="/media/2018/01/make-someone-smile-everyday.jpg" alt="" width="1024" height="686" /></a>

<strong>声明</strong>：大部分段子来自于博主收集于网络，无意侵权，记得每天都要学给自己和身边的人一个微笑 : )

<ol>
    <li>Jack："妮儿，弄啥嘞？" Rose："跳船！" Jack："败跳呗，那海水可凉啊！" Rose："海水可凉？有多凉？" Jack："可凉可凉了！败跳呗，你说你这个妮儿长得怪带劲嘞！"😄</li>
    <li>不是我针对谁，我是说在座的所有人，都是有品味的人。</li>
    <li>中午去吃火锅，看到火锅店的墙上醒目地写着： 羊是自己养的，菜是自己种的，油是自己榨的，提醒顾客放心食用。 买单的时候，我悄悄地跟老板说: 老板，这钱是我自己印的，请放心使用！ 老板追了我好几条街没追上，真有意思，腿是我自己长的，想往哪跑跑往哪跑，跑向充满希望的2018年！</li>
    <li>明人不说暗话，明猪不装暗B，今天我野猪佩琪把话撂这，我出去吃口猪食，回来要是没有人100个赞，我就拱翻在座各位，记住，是在座的所有人!!!</li>
</ol>''',
        'date': '2018-01-17'
    },
    {
        'title': '学点概念',
        'slug': 'basic-concepts',
        'content': '''<!-- wp:heading {"level":4} -->
<h4>1.菲涅尔方程：</h4>
<!-- /wp:heading -->

<!-- wp:image {"id":1254,"align":"center","linkDestination":"custom"} -->
<div class="wp-block-image"><figure class="aligncenter"><a href="/media/2018/09/Partial_transmittance.gif"><img src="/media/2018/09/Partial_transmittance.gif" alt="" class="wp-image-1254"/></a><figcaption>波部分的振幅经过由低到高反射率的介质的反射和折射</figcaption></figure></div>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>菲涅耳方程（或称菲涅耳条件）是由法国物理学家奥古斯丁·菲涅耳推导出的一组光学方程，用于描述光在两种不同折射率的介质中传播时的反射和折射。方程中所描述的反射因此还被称作"菲涅耳反射"。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":4} -->
<h4>2.莫尔条纹：</h4>
<!-- /wp:heading -->

<!-- wp:image {"id":1269,"align":"center","linkDestination":"custom"} -->
<div class="wp-block-image"><figure class="aligncenter"><a href="/media/2018/10/Moire02.gif"><img src="/media/2018/10/Moire02.gif" alt="" class="wp-image-1269"/></a></figure></div>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>莫列波纹（英语：Moiré pattern），又译为摩尔纹、莫尔条纹、叠纹、水状波纹，是一种在栅栏状条纹重叠下所产生的干涉影像。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":4} -->
<h4>3.Matlab中的数组基本概念：</h4>
<!-- /wp:heading -->

<!-- wp:image {"id":1289,"align":"center","linkDestination":"custom"} -->
<div class="wp-block-image"><figure class="aligncenter"><a href="/media/2018/11/ch_data_struct4_zh_CN.gif"><img src="/media/2018/11/ch_data_struct4_zh_CN.gif" alt="" class="wp-image-1289"/></a></figure></div>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>可以通过以下两个下标访问二维矩阵元素：第一个下标表示行索引，第二个下标表示列索引。多维数组使用其他下标进行索引。例如，三维数组使用以下三个下标：</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li>第一个下标引用数组维度 1（行）。</li><li>第二个下标引用维度 2（列）。</li><li>第三个引用维度 3（页）。</li></ul>
<!-- /wp:list -->

<!-- wp:heading {"level":4} -->
<h4>4.三角恒等式：</h4>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>在数学中，三角恒等式是对出现的所有值都为实变量，涉及到三角函数的等式。这些恒等式在表达式中有些三角函数需要简化的时候是很有用的。一个重要应用是非三角函数的积分。</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1399,"align":"center"} -->
<div class="wp-block-image"><figure class="aligncenter"><img src="/media/2018/12/2560px-Circle-trig6.svg-300x192.png" alt="" class="wp-image-1399"/><figcaption>在几何上依据以<em>O</em>为中心的单位圆可以构造角θ的很多三角函数</figcaption></figure></div>
<!-- /wp:image -->''',
        'date': '2018-09-10'
    },
    {
        'title': '隐私政策',
        'slug': 'privacy',
        'content': '''<!-- wp:heading -->
<h2>我们是谁</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>技术宅，程序员，我们的站点地址是：https://www.mspace.tech。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>我们收集何种及为何收集个人数据</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3>评论</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>当访客留下评论时，我们会收集评论表单所显示的数据，和访客的IP地址及浏览器的user agent字符串来帮助检查垃圾评论。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Cookies</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>如果您在我们的站点上留下评论，您可以选择用cookies保存您的姓名、电子邮件地址和网站。这是通过让您可以不用在评论时再次填写相关内容而向您提供方便。这些cookies会保留一年。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>我们保留多久您的信息</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>如果您留下评论，评论和其元数据将被无限期保存。我们这样做以便能识别并自动批准任何后续评论，而不用将这些后续评论加入待审队列。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>您对您的信息有什么权利</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>如果您有此站点的账户，或曾经留下评论，您可以请求我们提供我们所拥有的您的个人数据的导出文件，这也包括了所有您提供给我们的数据。您也可以要求我们抹除所有关于您的个人数据。</p>
<!-- /wp:paragraph -->''',
        'date': '2019-07-30'
    }
]


def import_pages():
    """导入页面数据"""
    # 获取首页
    home_page = HomePage.objects.first()
    if not home_page:
        print("错误：找不到首页，请先创建首页")
        return
    
    print(f"找到首页: {home_page}")
    
    # 导入每个页面
    for page_data in PAGES_DATA:
        title = page_data['title']
        slug = page_data['slug']
        content = page_data['content']
        
        # 检查页面是否已存在
        existing = CustomPage.objects.filter(slug=slug).first()
        if existing:
            print(f"跳过已存在的页面: {title}")
            continue
        
        # 创建新页面
        page = CustomPage(
            title=title,
            slug=slug,
            body=content
        )
        
        # 添加为首页的子页面
        home_page.add_child(instance=page)
        page.save_revision().publish()
        
        print(f"成功导入页面: {title}")
    
    print("\n所有页面导入完成！")


if __name__ == '__main__':
    import_pages()
