# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import subprocess
import sys

import simplejson as json
import re

import wx

# access_token
# access_token_secret
# consumer_key
# consumer_secret
from .credentials import *

app_running = True
all_names = set([""])


# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    def set_wx(self, master):
        self.master = master

    def on_data(self, data):
        data_json = json.loads(data)
        # print(data_json.keys())
        # print("[At:{} By:{}] {}".format(data_json['created_at'],
        # data_json['user']['screen_name'], data_json['text']))
        if "retweeted_status" not in data_json and data_json["lang"] == "en":
            ftext = (
                data_json["text"]
                .replace("\n", " ")
                .replace("&amp;", "-")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
            )

            out_user = data_json["user"]["screen_name"]
            out_content = ftext
            out_text = "[{}] {}".format(out_user, out_content)
            print(out_text)
            self.master.list_ctrl_1.Append(("", str(out_user), str(out_content)))
            new_names = re.findall("@\w+", ftext)
            global all_names
            all_names |= set(new_names)
            # print(all_names)

        if app_running:
            return True
        else:
            return False

    def on_error(self, status):
        print(status)
        if status == 420 or not app_running:
            # returning False in on_data disconnects the stream
            return False


gl_l = StdOutListener()
gl_auth = OAuthHandler(consumer_key, consumer_secret)
gl_auth.set_access_token(access_token, access_token_secret)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((517, 394))
        self.window_1_pane_1 = wx.Panel(self, wx.ID_ANY)
        self.text_ctrl_1 = wx.TextCtrl(self.window_1_pane_1, wx.ID_ANY, "")
        self.button_1 = wx.Button(self.window_1_pane_1, wx.ID_ANY, "Add label")
        self.window_1_pane_2 = wx.Panel(self, wx.ID_ANY)
        self.list_ctrl_1 = wx.ListCtrl(
            self.window_1_pane_2, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
        )
        self.list_box_1 = wx.ListBox(
            self.window_1_pane_2, wx.ID_ANY, choices=["#btc", "cryptocurrency"]
        )
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.button_2 = wx.Button(self.panel_1, wx.ID_ANY, "Refresh labels")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.insert_label, self.button_1)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.remove_label, self.list_box_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_labels, self.button_2)
        self.stream = None
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("frame")
        self.list_ctrl_1.AppendColumn("Time", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_1.AppendColumn("Name", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.list_ctrl_1.AppendColumn("Content", format=wx.LIST_FORMAT_LEFT, width=210)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.text_ctrl_1, 1, wx.ALL | wx.EXPAND, 2)
        sizer_2.Add(self.button_1, 0, 0, 0)
        self.window_1_pane_1.SetSizer(sizer_2)
        sizer_1.Add(self.window_1_pane_1, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.list_ctrl_1, 2, wx.EXPAND, 0)
        grid_sizer_1.Add(self.list_box_1, 0, wx.EXPAND, 0)
        self.window_1_pane_2.SetSizer(grid_sizer_1)
        sizer_1.Add(self.window_1_pane_2, 2, wx.ALIGN_CENTER | wx.EXPAND, 0)
        sizer_3.Add(self.button_2, 0, wx.ALL, 2)
        label_2 = wx.StaticText(self.panel_1, wx.ID_ANY, "No messages")
        sizer_3.Add(label_2, 1, wx.ALIGN_CENTER | wx.ALL, 2)
        self.panel_1.SetSizer(sizer_3)
        sizer_1.Add(self.panel_1, 0, wx.EXPAND, 1)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def insert_label(self, event):  # wxGlade: MyFrame.<event_handler>
        txt = self.text_ctrl_1.GetLineText(0)
        self.list_box_1.InsertItems([txt], 0)
        self.text_ctrl_1.Clear()

    def remove_label(self, event):  # wxGlade: MyFrame.<event_handler>
        self.list_box_1.Delete(self.list_box_1.FindString(event.String))

    def refresh_labels(self, event):  # wxGlade: MyFrame.<event_handler>
        # This handles Twitter authetification and the connection to Twitter Streaming API
        gl_l.set_wx(self)

        if self.stream is not None:
            self.stream.disconnect()
        self.stream = Stream(gl_auth, gl_l)

        filter_items = []
        for i in range(self.list_box_1.GetCount()):
            filter_items.append(self.list_box_1.GetString(i))

        print(filter_items)
        self.stream.filter(track=filter_items, is_async=True)
        print("New stream initialized.")


# end of class MyFrame


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


def wxapp():
    app = MyApp(0)
    app.MainLoop()
    return app


# end of class MyApp

if __name__ == "__main__":
    wxapp()
