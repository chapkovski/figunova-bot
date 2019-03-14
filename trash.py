import chartify

# Blank charts tell you how to fill in the labels
ch = chartify.Chart()
# print(ch)
import tempfile
contents = ch._figure_to_svg()
tf = tempfile.NamedTemporaryFile()
tfName = tf.name
tf.seek(0)
tf.write(contents)
# tf.flush()

