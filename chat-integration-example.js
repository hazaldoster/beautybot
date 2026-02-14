#!/usr/bin/env node

/**
 * Sohbet Entegrasyon Örneği
 * 
 * Bu script, güzellik ürünleri API'sinin bir sohbet arayüzüyle nasıl entegre edileceğini gösterir.
 * Bir güzellik ürünleri sohbet robotuyla bir konuşmayı simüle eder.
 */

const beautyApi = require('./beauty-api');

// Bir sohbet konuşmasını simüle et
async function sohbetiSimuleEt() {
  console.log('🤖 Güzellik Ürünleri Sohbet Robotu');
  console.log('==================================');
  console.log('');
  
  // Karşılama mesajı
  console.log('🤖 Güzellik Asistanı\'na hoş geldiniz! Size güzellik ürünleri bulma, öneriler alma ve kozmetik ürünleri hakkında sorular yanıtlama konusunda yardımcı olabilirim. Bugün ne arıyorsunuz?');
  console.log('');
  
  // Kullanıcı sorgularını ve bot yanıtlarını simüle et
  const sorgular = [
    "Bana kaş maskarası önerir misin?",
    "En iyi ruj markaları nelerdir?",
    "En yüksek puanlı makyaj ürünleri göster",
    "Maybelline kaş ürünleri var mı?",
    "Kalıcı fondöten arıyorum"
  ];
  
  for (const sorgu of sorgular) {
    // Kullanıcı mesajını simüle et
    console.log(`👤 ${sorgu}`);
    
    // Sorguyu güzellik API'si kullanarak işle
    const yanit = await beautyApi.processUserQuery(sorgu);
    
    // Bot yanıtını simüle et
    console.log(`🤖 ${yanit}`);
    console.log('');
  }
  
  // Bir ürün önerisi akışını simüle et
  console.log('👤 NYX marka bir kaş ürünü arıyorum. Önerebilir misiniz?');
  
  // Ürünü ara
  const aramaSonuclari = await beautyApi.searchProducts('NYX kas', 3);
  
  if (aramaSonuclari.length > 0) {
    console.log('🤖 İşte NYX marka kaş ürünleri:');
    aramaSonuclari.forEach((urun, index) => {
      console.log(`   ${index + 1}. ${urun.name} - Fiyat: ${urun.price}`);
    });
    
    // Bir ürün seçildiğini simüle et
    const seciliUrun = aramaSonuclari[0];
    console.log(`\n👤 ${seciliUrun.name} ürünü hakkında daha fazla bilgi alabilir miyim?`);
    
    // Ürün detaylarını formatla
    const urunDetaylari = beautyApi.formatProductForChat(seciliUrun);
    console.log(`🤖 ${urunDetaylari}`);
    
    // Benzer ürünleri öner
    console.log('\n🤖 Bu ürüne benzer başka ürünler de ilginizi çekebilir:');
    const oneriler = await beautyApi.getProductRecommendations(seciliUrun.product_id, 2);
    
    if (oneriler.length > 0) {
      oneriler.forEach((oneri, index) => {
        console.log(`   ${index + 1}. ${oneri.name} - Fiyat: ${oneri.price}`);
      });
    } else {
      console.log('   Şu anda benzer ürün önerisi bulunamadı.');
    }
  } else {
    console.log('🤖 Üzgünüm, NYX marka kaş ürünü bulamadım. Başka bir marka denemek ister misiniz?');
  }
  
  console.log('');
  console.log('👤 Kaş maskarası nasıl uygulanır?');
  console.log('🤖 Kaş maskarası uygulama adımları:');
  console.log('   1. Kaşlarınızı önce kaş fırçasıyla tarayın');
  console.log('   2. Maskarayı kaşlarınızın doğal yönünde, yukarı doğru uygulayın');
  console.log('   3. Fazla ürünü almak için fırçayı tüpün ağzında sıyırın');
  console.log('   4. İnce, hafif hareketlerle uygulayın');
  console.log('   5. Kurumadan önce kaşlarınızı tekrar tarayarak şekillendirin');
  console.log('');
  
  console.log('👤 Teşekkür ederim, çok yardımcı oldunuz!');
  console.log('🤖 Rica ederim! Başka güzellik ürünleri veya makyaj teknikleri hakkında sorularınız olursa bana sorabilirsiniz. İyi günler dilerim!');
}

// Sohbet simülasyonunu çalıştır
sohbetiSimuleEt(); 