#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2015-2016 Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from gprime.lib import Event
from gprime.utils.id import create_id

import tornado.web
import json
import html

from .handlers import BaseHandler
from ..forms import EventForm

class EventHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path=""):
        """
        HANDLE
        HANDLE/edit|delete
        /add
        b2cfa6ca1e174b1f63d/remove/eventref/1
        """
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1) or 1)
        search = self.get_argument("search", "")
        if "/" in path:
            handle, action= path.split("/", 1)
        else:
            handle, action = path, "view"
        if handle:
            if handle == "add":
                event = Event()
                action = "edit"
            else:
                event = self.database.get_event_from_handle(handle)
            if event:
                if action == "delete":
                    form = EventForm(self, instance=event)
                    form.delete()
                    return
                else:
                    self.render("event.html",
                                **self.get_template_dict(tview=_("event detail"),
                                                         action=action,
                                                         page=page,
                                                         search=search,
                                                         form=EventForm(self, instance=event)))
                    return
            else:
                self.clear()
                self.set_status(404)
                self.finish("<html><body>No such event</body></html>")
                return
        form = EventForm(self)
        try:
            form.select(page, search)
        except Exception as exp:
            self.send_message(str(exp))
            self.redirect(form.make_url())
            return
        self.render("page_view.html",
                    **self.get_template_dict(tview=_("event view"),
                                             page=page,
                                             search=search,
                                             form=form,
                                         )
                )

    @tornado.web.authenticated
    def post(self, path):
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1) or 1)
        search = self.get_argument("search", "")
        if "/" in path:
            handle, action = path.split("/")
        else:
            handle, action = path, "view"
        json_data = json.loads(html.unescape(self.get_argument("json_data")))
        instance = Event.from_struct(json_data)
        update_json = self.get_argument("update_json", None)
        if update_json:
            # edit the instance
            self.update_instance(instance, update_json)
            form = EventForm(self, instance=instance)
            form.load_data()
            self.render("event.html",
                        **self.get_template_dict(tview=_("event detail"),
                                                 action=action,
                                                 page=page,
                                                 search=search,
                                                 form=form))
        else:
            self.send_message("Updated event. <a href=\"FIXME\">Undo</a>")
            form = EventForm(self, instance=instance)
            form.save()
            handle = instance.handle
            self.redirect(self.app.make_url("/event/%(handle)s" % {"handle": handle}))

