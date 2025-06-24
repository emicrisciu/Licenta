# Sistem pentru urmărirea în timp real a poziției mingii pe terenul de fotbal și detecția depășirii liniilor de margine

## Adresa repository-ului

https://github.com/emicrisciu/Licenta

## Organizarea celor mai importante fișiere

* Directorul _**Arduino**_ conține programul dezvoltat în editorul de cod _Arudino IDE_, care rulează pe microcontrolerul _ESP32_
* Directorul _**Python**_ conține fișierele _.py_ ce cuprind implementarea aplicației de nivel înalt
* Directorul _**UWB**_ conține pachetul cu firmware-ul de bază ce este descărcat pe senzorii _UWB_

## Pașii de lansare a aplicației

* Aplicația este dezvoltată în limbajul de programare _Python_, așadar trebuie ca un mediu virtual de _Python_ să fie instalat în prealabil
* Mediul virtual se poate instala doar dacă _Python_ este instalat mai întâi
* Cum aplicația este dezvoltată pe placa _Raspberry Pi_, voi prezenta pașii ce se execută pe aceasta
<br>

1. Python poate fi descărcat de aici: https://www.python.org/downloads/
2. Pentru crearea mediului virtual se introduce în terminal `python -m venv nume_mediu`
3. Pentru activarea mediului virtual se tastează `source nume_mediu/bin/activate`
4. Pentru instalarea oricărui pachet necesar execuției programului se poate introduce `pip install nume_pachet`
5. Pentru lansarea în execuție a aplicației este folosită comanda `python program_principal.py`
6. Aplicația se oprește prin închiderea ferestrei ce cuprinde graficul sub forma unui teren de fotbal
7. La final, pentru dezactivarea mediului virtual, se execută comanda `deactivate`