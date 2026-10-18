/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2018 University of Washington
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <iostream>
#include "ns3/command-line.h"

using namespace ns3;

int main (int argc, char *argv[])
{
  std::string language = "English";
  std::string phrase;

  CommandLine cmd;
  cmd.AddValue ("language", "Specify language", language);
  cmd.Parse (argc, argv);

  if (language == "English")
    {
      phrase = "Hello world";
    }
  else if (language == "Spanish")
    {
      phrase = "Hola mundo";
    }
  else
    {
      phrase = "I don't understand";
    }

  std::cout << phrase << std::endl;
}
