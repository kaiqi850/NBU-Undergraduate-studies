/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2007 University of Washington
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

#ifndef DROP_HEAD_QUEUE_H
#define DROP_HEAD_QUEUE_H

#include "ns3/queue.h"

namespace ns3 {

/**
 * \ingroup queue
 *
 * \brief A FIFO packet queue that drops packets at the head of the queue on overflow
 */
template <typename Item>
class DropHeadQueue : public Queue<Item>
{
public:
  /**
   * \brief Get the type ID.
   * \return the object TypeId
   */
  static TypeId GetTypeId (void);
  /**
   * \brief DropHeadQueue Constructor
   *
   * Creates a droptail queue with a maximum size of 100 packets by default
   */
  DropHeadQueue ();

  virtual ~DropHeadQueue ();

  virtual bool Enqueue (Ptr<Item> item);
  virtual Ptr<Item> Dequeue (void);
  virtual Ptr<Item> Remove (void);
  virtual Ptr<const Item> Peek (void) const;

private:
  using Queue<Item>::Head;
  using Queue<Item>::Tail;
  using Queue<Item>::DoEnqueue;
  using Queue<Item>::DoDequeue;
  using Queue<Item>::DoRemove;
  using Queue<Item>::DoPeek;

  NS_LOG_TEMPLATE_DECLARE;     //!< redefinition of the log component
};


/**
 * Implementation of the templates declared above.
 */

template <typename Item>
TypeId
DropHeadQueue<Item>::GetTypeId (void)
{
  static TypeId tid = TypeId (("ns3::DropHeadQueue<" + GetTypeParamName<DropHeadQueue<Item> > () + ">").c_str ())
    .SetParent<Queue<Item> > ()
    .SetGroupName ("Network")
    .template AddConstructor<DropHeadQueue<Item> > ()
  ;
  return tid;
}

template <typename Item>
DropHeadQueue<Item>::DropHeadQueue () :
  Queue<Item> (),
  NS_LOG_TEMPLATE_DEFINE ("DropHeadQueue")
{
  NS_LOG_FUNCTION (this);
}

template <typename Item>
DropHeadQueue<Item>::~DropHeadQueue ()
{
  NS_LOG_FUNCTION (this);
}

template <typename Item>
bool
DropHeadQueue<Item>::Enqueue (Ptr<Item> item)
{
  NS_LOG_FUNCTION (this << item);

  return DoEnqueue (Tail (), item);
}

template <typename Item>
Ptr<Item>
DropHeadQueue<Item>::Dequeue (void)
{
  NS_LOG_FUNCTION (this);

  Ptr<Item> item = DoDequeue (Head ());

  NS_LOG_LOGIC ("Popped " << item);

  return item;
}

template <typename Item>
Ptr<Item>
DropHeadQueue<Item>::Remove (void)
{
  NS_LOG_FUNCTION (this);

  Ptr<Item> item = DoRemove (Head ());

  NS_LOG_LOGIC ("Removed " << item);

  return item;
}

template <typename Item>
Ptr<const Item>
DropHeadQueue<Item>::Peek (void) const
{
  NS_LOG_FUNCTION (this);

  return DoPeek (Head ());
}

} // namespace ns3

#endif /* DROP_HEAD_QUEUE_H */
