#if CONFIG_FREERTOS_UNICORE
#define ARDUINO_RUNNING_CORE 0
//static const BaseType_t  ARDUINO_RUNNING_CORE = 0
#else
#define ARDUINO_RUNNING_CORE 1
//static const BaseType_t  ARDUINO_RUNNING_CORE = 1
#endif

#include <DHT.h>

// Broche de données du capteur DHT11
#define DHTPIN 0
#define DHTTYPE DHT11

// Broche de la LED
const int LED_PIN = 4;


// Création de l'objet DHT
DHT dht(DHTPIN, DHT11);



void setup() {
  Serial.begin(115200);
  dht.begin();

  // Initialisation des tâches
  xTaskCreatePinnedToCore(SensorTask, "SensorTask", 10000, NULL, 1, NULL, 0);  // Crée la tâche du capteur DHT11 sur le cœur 0
  xTaskCreatePinnedToCore(LedTask, "LedTask", 1000, NULL, 1, NULL, 1);  // Crée la tâche de la LED sur le cœur 1

}

void loop() {
  // La boucle de la carte ESP32 doit rester vide
  // Les tâches sont gérées par FreeRTOS
}


// Fonction exécutée par la tâche du capteur DHT11
void SensorTask(void *pvParameters) {
  while (1) {
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Erreur lors de la lecture du capteur DHT11");
    } else {
      Serial.println((String) temperature + "x" + (String) humidity );
    }
    // Serial.flush();
    vTaskDelay(1000 / portTICK_PERIOD_MS);  // Délai d'attente de 1 seconde
    
  }
}

// Fonction exécutée par la tâche de la LED
void LedTask(void *pvParameters) {
  pinMode(LED_PIN, OUTPUT);

  while (1) {

      if (Serial.available()>0)
    {
      char x = Serial.read();

      if ( x == '1')
      {
          
          digitalWrite (LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
          digitalWrite(LED_PIN, HIGH);   // Allume la LED
          // vTaskDelay(500 / portTICK_PERIOD_MS);  // Délai d'attente de 500 ms
          // Serial.println('1');
          // delay (1000);  // wait for a second
          // Serial.flush();

      }

      if ( x == '0')
      {
        
          digitalWrite (LED_BUILTIN, LOW); // turn the LED off by making the voltage LOW
          digitalWrite(LED_PIN, LOW);    // Éteint la LED
          Serial.flush();
          // vTaskDelay(500 / portTICK_PERIOD_MS);  // Délai d'attente de 500 ms
          // Serial.println('0');
      // delay (1000); 
      }
    }
    
  }
}

