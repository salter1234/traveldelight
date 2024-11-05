document.addEventListener("DOMContentLoaded", function() {
    const tabs = document.querySelectorAll(".tab-btn");
    const spotsContainer = document.querySelector(".spots");
    const regionMap = document.getElementById("regionMap");

    // 替換為正確的靜態路徑
    const imagePath = "/static/pictures/";

    // 設置點擊事件以加載更多內容
    document.getElementById('loadMore').addEventListener('click', function() {

    });

    // 設置每個選項卡的點擊事件
    tabs.forEach(tab => {
        tab.addEventListener("click", function() {
            document.querySelector(".tab-btn.active").classList.remove("active");
            this.classList.add("active");

            const region = this.dataset.region;
            fetchSpots(region);
        });
    });

    function fetchSpots(region) {
        // 更換地圖圖片
        switch (region) {
            case "north":
                regionMap.src = `${imagePath}twmapnorth.png`;
                spotsContainer.innerHTML = `<div class="region-info">
                                                <b><p style="color: #111111;">「北部地區」包括臺北市、新北市、基隆市、宜蘭縣、桃園市、新竹縣及新竹市等7個縣市。您可以從臺灣最高樓——臺北101俯瞰臺北美景；前往故宮博物院一窺歷史典藏文物瑰寶；或走進知名老街如：九份、淡水、鶯歌、三峽等感受古街風情記憶。</p></b>
                                                <div class="images">
                                                    <img src="/static/pictures/section/north1.jpg" alt="北部景點1" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/north2.jpg" alt="北部景點2" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/north3.jpg" alt="北部景點3" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/north4.jpg" alt="北部景點4" style="width: 24%; margin: 1%;">
                                                </div>
                                            </div>`;
                break;
            case "central":
                regionMap.src = `${imagePath}twmapcentral.png`;
                spotsContainer.innerHTML = `<div class="region-info">
                                                <b><p style="color: #111111;">「中部地區」包括苗栗縣、臺中市、彰化縣、南投縣及雲林縣等5個縣市，位於臺灣心臟地帶，常年氣候舒適，尤其是臺中市，四季氣溫宜人，非常適合旅行。中部地區擁有多處老少皆宜的渡假村及遊樂中心，包含苗栗西湖渡假村、臺中麗寶樂園、南投泰雅渡假村、九族文化村及雲林劍湖山世界等。喜歡文藝的朋友們不可錯過苗栗的木雕與燒陶藝術，可自己動手DIY實作體驗一番，臺中市國立臺灣美術館與自然科學博物館推薦遊客進入細細參觀，雲林縣是揚名世界的布袋戲演藝文化發源地，值得深入欣賞。</p></b>
                                                <div class="images">
                                                    <img src="/static/pictures/section/central1.jpg" alt="中部景點1" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/central2.jpg" alt="中部景點2" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/central3.jpg" alt="中部景點3" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/central4.jpg" alt="中部景點4" style="width: 24%; margin: 1%;">
                                                </div>
                                            </div>`;
                break;
            case "south":
                regionMap.src = `${imagePath}twmapsouth.png`;
                spotsContainer.innerHTML = `<div class="region-info">
                                                <b><p style="color: #111111;">臺灣南部地區散發著濃厚的歷史文化，臺南市是全臺歷史最悠久的文化古都，十九世紀末期前，臺南一直是臺灣政治經濟文化重心，古蹟名勝特別多。嘉義縣因北回歸線通過而建造的「北回歸線天文廣場」，呈現北回歸線的地理象徵。阿里山森林遊樂區舉世聞名，高山森林鐵路及深藏不露的林間古道，吸引大批國內外遊客造訪，而阿里山雲海、日出、晚霞等自然美景，遠近馳名，是旅遊臺灣必遊的重點景點之一。</p><p style="color: #111111;">臺灣南部氣候四季如夏，位於屏東有「臺灣南洋」之稱的墾丁公園，得天獨厚，浮潛融入海中美景、暢玩水上新潮活動，再前往臺灣最南端的「鵝鑾鼻」，左看太平洋右覽臺灣海峽的壯碩景觀。</p></b>
                                                <div class="images">
                                                    <img src="/static/pictures/section/south1.jpg" alt="南部景點1" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/south2.jpg" alt="南部景點2" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/south3.jpg" alt="南部景點3" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/south4.jpg" alt="南部景點4" style="width: 24%; margin: 1%;">
                                                </div>
                                            </div>`;
                break;
            case "east":
                regionMap.src = `${imagePath}twmapeast.png`;
                spotsContainer.innerHTML = `<div class="region-info">
                                                <b><p style="color: #111111;">臺灣東部地區包含花蓮縣及臺東縣2個縣市，東臨浩瀚太平洋，西倚中央山脈，擁有臨山面海的優越地理位置，最初葡萄牙人航行經過臺灣東部海岸時，看見壯麗的山川美景呈現於眼前，驚呼「FORMOSA」（美極了），臺灣「福爾摩沙」的稱號由此而來，東部極致的天然美景也由此可見。東部地區擁有豐富的生態資源、悠久的農業文化和純樸善良的在地居民，是臺灣的「後花園」，非常適合慢活養生之旅，行走在這塊淨土上，放慢你的呼吸頻率，大口吸入甜甜的空氣香，long stay是最好的行程安排。</p><p style="color: #111111;">太魯閣公園是臺灣必遊景點，以峽谷景觀聞名，雄偉壯麗的山川景色，多處景點展現出原始的險峻地形與奧妙的地質面貌。東部的秀姑巒溪，河道迂迴，切穿海岸山脈，形成峽谷與曲流，刺激又有挑戰的泛舟活動吸引無數年輕人留下最英雄的回憶。</p></b>
                                                <div class="images">
                                                    <img src="/static/pictures/section/east1.jpg" alt="東部景點1" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/east2.jpg" alt="東部景點2" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/east3.jpg" alt="東部景點3" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/east4.jpg" alt="東部景點4" style="width: 24%; margin: 1%;">
                                                </div>
                                            </div>`;
                break;
            case "island":
                regionMap.src = `${imagePath}twmapisland.png`;
                spotsContainer.innerHTML = `<div class="region-info">
                                                <b><p style="color: #111111;">臺灣主要島嶼之外，周邊的小島也為數可觀，澎湖、金門與連江三個縣市位於離島地區，原本曾神秘的軍事管制禁區——金門，開放觀光後成為熱絡的旅遊地區，具鄉土風味的金門特產三寶，鋼刀、貢糖、高粱酒，總讓人滿載而歸，而馬祖的老酒、八八坑道高粱、大麯酒，更令人齒頰留香。既是外島，各樣生鮮美饌種類繁多，讓遊客得以飽嘗頂級海鮮美味。澎湖，春夏花火節火樹銀花綻放熱情和浪漫，碧海藍天與柔白細緻沙灘的雙重享受，加上各式各樣的新潮有趣的沙灘水上遊樂設施，讓你盡情的享受水上世界。</p></b>
                                                <div class="images">
                                                    <img src="/static/pictures/section/island1.jpg" alt="外島景點1" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/island2.jpg" alt="外島景點2" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/island3.jpg" alt="外島景點3" style="width: 24%; margin: 1%;">
                                                    <img src="/static/pictures/section/island4.jpg" alt="外島景點4" style="width: 24%; margin: 1%;">
                                                </div>
                                            </div>`;
                break;
            default:
                regionMap.src = "/static/pictures/default.png"; // 預設圖片
                spotsContainer.innerHTML = `<div>未選擇任何區域，請選擇一個區域查看熱門景點。</div>`;
        }

        // 確保圖片尺寸正確
        const images = spotsContainer.querySelectorAll("img");
        images.forEach(img => {
            img.onload = () => {
                img.style.width = "20%"; // 調整圖片寬度
                img.style.height = "130px";
                img.style.margin = "1%"; // 調整圖片邊距
            };
        });

        // 設定 div 的樣式
        const regionInfoDiv = spotsContainer.querySelector('.region-info');
        if (regionInfoDiv) {
            regionInfoDiv.style.position = "absolute"; // 使用絕對定位
            regionInfoDiv.style.top = "130px";
            regionInfoDiv.style.left = "0px";
            regionInfoDiv.style.textAlign = "left"; // 讓文字靠左對齊
            regionInfoDiv.style.padding = "20px"; // 設定內邊距
            regionInfoDiv.style.border = "1px solid #ccc"; // 設定邊框
            regionInfoDiv.style.borderRadius = "5px"; // 設定圓角
            regionInfoDiv.style.boxShadow = "0 2px 5px rgba(0, 0, 0, 0.1)"; // 設定陰影
            regionInfoDiv.style.textIndent = "60px"; // 設定文字縮排
            regionInfoDiv.style.width = "70%"; // 設定框的寬度為 70%
        }
    }



    // 當地圖圖片無法加載時使用預設圖片
    // regionMap.onerror = function() {
    //     regionMap.src = "/static/pictures/default.png"; // 預設圖片
    // };
});