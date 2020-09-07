# Russian-document-parser
# Распознование Российских ИНН
На данный момент реализовано распознавание ИНН, на вход можно подавать файлы формата .jpg, .png и .pdf. 

```python
from Parse_INN import INN_parser

file = "инн.jpg" 
parser = INN_parser()
parser.set_image(file)
print(parser.find_INN())
```

Есть два возможных режима работы, с использование библиотеки pyteseract (Инструкция по установке https://github.com/h/pytesseract), и с помощью кастомных нейронных сетей, по умолчанию используется tesseract.
Для использования кастомной нейронной сети:
```python
parser = INN_parser("NN")
```
На данный момент в проекте находится обученная модель (python notebook) для задачи MNIST (точность ~99.9%), однако для печатных цифр она работает не очень хорошо. 
Для улучшения качества работы следует обучить модель на других данных. В целом логика работы правильная, ИНН в хорошем качестве распознаются примерно в 95% случаев (для tesseract).  