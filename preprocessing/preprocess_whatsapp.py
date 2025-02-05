import datetime
import re
import os

import pandas as pd

DATE_RE = '\\d\\d?/\\d\\d?/\\d\\d?'
TIME_RE = '\\d\\d?:\\d\\d? [AP]M'
SENDER_RE = '[ a-zA-Z0-9]+'
MSG_RE = re.compile(f'(?P<date>{DATE_RE}), (?P<time>{TIME_RE}) - (?P<sender>{SENDER_RE}): (?P<message>.+)')

WHATSAPP_LOG_DIR = '../data/WhatsAppRaw/'
WHATSAPP_RESULTS_DIR = '../data/WhatsAppCleaned/'


def create_str_from_log_file(log_file):
  content = ''
  with open(log_file, 'r', encoding='utf-8') as file:
    for line in file:
      line = line.strip()
      line = re.sub(r' ', ' ', line, flags=re.UNICODE)
      if MSG_RE.match(line):
        if content != '':
          content += '\n'
        content += line
      else:
        content += ' '
        content += line
    return content


def create_df_from_str(content):
  date_times = []
  senders = []
  messages = []
  raw = []

  for match in MSG_RE.finditer(content):
    date_times.append(f'{match[1]} {match[2]}')
    senders.append(match[3])
    messages.append(match[4])
    raw.append(match[0])

  res_df = pd.DataFrame({'DATETIME': date_times, 'SENDER': senders, 'MESSAGE': messages, 'RAW': raw})
  res_df['DATETIME'].apply(lambda x: datetime.datetime.strptime)
  return res_df


def combine_same_sender(chat_df, col_to_combine='MESSAGE', col_to_groupby='SENDER',
                        cols_to_agg=set(), cols_to_keep={'DATETIME'}):
  """
  Combines values in chat_df[col_to_combine] while chat_df[col_to_groupby] is constant.
  Additionally, aggregates chat_df[cols_to_agg] into sets

  utility: combine contiguous messages from the same sender

  :param chat_df: a pd.DataFrame containing chat data, created by `create_df_from_str()`
  :param col_to_combine: column name of values to be combined
  :param col_to_groupby: column name of IDs to group by
  :param cols_to_agg: (optional) column name of values to be aggregated into sets
  :return: processed DF
  """

  # source: https://www.java-tech-stack.com/post/27180
  # Identify groups where the value changes
  chat_df['group'] = (chat_df[col_to_groupby] != chat_df[col_to_groupby].shift()).cumsum()

  chat_df = chat_df.groupby('group', as_index=False).agg({
    col_to_groupby: 'first',
    col_to_combine: '\n'.join,
    **{c: set for c in cols_to_agg},
    **{c: 'first' for c in cols_to_keep}
  }).reset_index(drop=True)

  return chat_df.drop(columns=['group'])


def add_context(chat_df, col_to_cat='RAW', new_col_name='FULL_CONTEXT', context_len=3):
  neg_cols_added = [f'{col_to_cat}_neg_{i}' for i in range(1, 1 + context_len)]
  plus_cols_added = [f'{col_to_cat}_plus_{i}' for i in range(1, 1 + context_len)]

  for i in range(1, context_len + 1):
    chat_df[f'{col_to_cat}_neg_{i}'] = chat_df[col_to_cat].shift(-i)
    chat_df[f'{col_to_cat}_plus_{i}'] = chat_df[col_to_cat].shift(i)

  chat_df[new_col_name] = chat_df[[*neg_cols_added, col_to_cat, *plus_cols_added]].fillna('').agg('\n'.join,
                                                                                                  axis=1).str.strip()
  chat_df.drop(columns=[*neg_cols_added, *plus_cols_added], inplace=True)


if __name__ == '__main__':
    for filename in os.listdir(WHATSAPP_LOG_DIR):
      if filename.endswith('.txt'):
        chat_name = filename[len('WhatsApp Chat with '):-len('.txt')]
        log_file = os.path.join(WHATSAPP_LOG_DIR, filename)
        content = create_str_from_log_file(log_file)
        log_df = create_df_from_str(content)
        log_df = combine_same_sender(log_df)
        log_df['PLATFORM'] = 'WhatsApp'
        log_df['CHAT'] = chat_name
        log_df['MSG_ID'] = 'WA ' + chat_name + ' '
        log_df['MSG_ID'] = log_df['MSG_ID'].str.cat(log_df.index.astype(str))
        # add_context(log_df)

        log_df.to_csv(os.path.join(WHATSAPP_RESULTS_DIR, f'{chat_name}.csv'), index=False)

    csv_fnames_to_cat = [fname for fname in os.listdir(WHATSAPP_RESULTS_DIR) if fname != 'Temp.csv']
    combined_df = pd.concat([pd.read_csv(os.path.join(WHATSAPP_RESULTS_DIR, file)) for file in csv_fnames_to_cat])
    combined_df.to_csv(os.path.join(WHATSAPP_RESULTS_DIR, 'WhatsAppCombined.csv'), index=False)
